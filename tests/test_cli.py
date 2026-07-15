from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired
from unittest import mock

from freedom_os_manager.adapters import agents
from freedom_os_manager.cli import main


def write(path: Path, content: str = "# readme\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class CliTests(unittest.TestCase):
    def test_cli_scan_list_status_doctor_install_uninstall(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write(root / "skills" / "freedom-os-manager" / "SKILL.md")
            registry = root / ".freedom-os" / "registry" / "capabilities.json"

            code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "scan"])
            self.assertEqual(code, 0)
            self.assertIn("Discovered 1 capabilities", output)

            code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "cap", "list"])
            self.assertEqual(code, 0)
            self.assertIn("freedom-os-manager", output)

            code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "status", "freedom-os-manager"])
            self.assertEqual(code, 0)
            self.assertIn("runtime:", output)

            with mock.patch("freedom_os_manager.doctor.hermes.skill_installed", return_value=(False, "hermes command not found")):
                code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "doctor", "freedom-os-manager"])
            self.assertEqual(code, 1)
            self.assertIn("skill_file", output)
            self.assertIn("doctor_status=failed", output)

            with mock.patch("freedom_os_manager.cli.agents.available_agents", return_value=["codex", "hermes"]):
                code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "install", "freedom-os-manager", "--dry-run"])
            self.assertEqual(code, 0)
            self.assertIn("dry_run=true", output)
            self.assertIn("-a codex -a hermes-agent", output)

            code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "uninstall", "freedom-os-manager"])
            self.assertEqual(code, 0)
            self.assertIn("preview=true", output)
            self.assertIn("No source files", output)

    def test_install_executes_for_detected_codex_and_hermes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write(root / "skills" / "demo" / "SKILL.md")
            registry = root / ".freedom-os" / "registry" / "capabilities.json"

            with (
                mock.patch("freedom_os_manager.cli.agents.available_agents", return_value=["codex", "hermes"]),
                mock.patch("freedom_os_manager.cli.agents.npx_available", return_value=True),
                mock.patch(
                    "freedom_os_manager.cli.agents.install_skill",
                    return_value=CompletedProcess(args=[], returncode=0, stdout="installed\n", stderr=""),
                ) as install_skill,
            ):
                code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "install", "demo"])

            self.assertEqual(code, 0)
            self.assertIn("install_exit_code=0", output)
            install_skill.assert_called_once()
            self.assertEqual(install_skill.call_args.args[1], ["codex", "hermes"])

            code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "status", "demo"])
            self.assertEqual(code, 0)
            self.assertIn("codex.skill_installed: True", output)
            self.assertIn("hermes.skill_installed: True", output)

    def test_uninstall_execute_does_not_mark_success_on_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write(root / "skills" / "demo" / "SKILL.md")
            registry = root / ".freedom-os" / "registry" / "capabilities.json"
            run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "scan"])

            with (
                mock.patch("freedom_os_manager.cli.agents.available_agents", return_value=["hermes"]),
                mock.patch("freedom_os_manager.cli.agents.npx_available", return_value=True),
                mock.patch(
                    "freedom_os_manager.cli.agents.uninstall_skill",
                    return_value=CompletedProcess(args=[], returncode=9, stdout="", stderr="failed\n"),
                ),
            ):
                code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "uninstall", "demo", "--execute"])

            self.assertEqual(code, 9)
            self.assertIn("uninstall_exit_code=9", output)

            code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "status", "demo"])
            self.assertEqual(code, 0)
            self.assertIn("status: broken", output)

    def test_sync_installed_replaces_registry_with_local_installed_skills_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            local_skills = Path(temp_dir) / "installed-skills"
            registry = Path(temp_dir) / ".freedom-os" / "registry" / "capabilities.json"
            write(root / "skills" / "installed-hybrid" / "SKILL.md")
            write(root / "services" / "installed-hybrid" / "README.md")
            write(root / "projects" / "installed-hybrid" / "README.md")
            write(root / "skills" / "repo-only" / "SKILL.md")
            write(local_skills / "installed-hybrid" / "SKILL.md")
            write(local_skills / "lark-task" / "SKILL.md")

            run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "scan"])
            code, output = run_cli(
                [
                    "--repo-root",
                    str(root),
                    "--registry",
                    str(registry),
                    "capabilities",
                    "sync-installed",
                    "--local-skill-root",
                    str(local_skills),
                ]
            )

            self.assertEqual(code, 0)
            self.assertIn("Installed capabilities saved: 2", output)
            code, output = run_cli(["--repo-root", str(root), "--registry", str(registry), "capabilities", "list"])
            self.assertEqual(code, 0)
            self.assertIn("installed-hybrid", output)
            self.assertIn("hybrid-service", output)
            self.assertIn("lark-task", output)
            self.assertNotIn("repo-only", output)

    def test_check_installed_reports_drift_and_fix_syncs_registry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "repo"
            local_skills = Path(temp_dir) / "installed-skills"
            registry = Path(temp_dir) / ".freedom-os" / "registry" / "capabilities.json"
            write(root / "skills" / "demo" / "SKILL.md")
            write(local_skills / "demo" / "SKILL.md")
            write(local_skills / "lark-task" / "SKILL.md")

            code, output = run_cli(
                [
                    "--repo-root",
                    str(root),
                    "--registry",
                    str(registry),
                    "capabilities",
                    "check-installed",
                    "--local-skill-root",
                    str(local_skills),
                ]
            )
            self.assertEqual(code, 1)
            self.assertIn("missing_in_registry=2", output)

            code, output = run_cli(
                [
                    "--repo-root",
                    str(root),
                    "--registry",
                    str(registry),
                    "capabilities",
                    "check-installed",
                    "--local-skill-root",
                    str(local_skills),
                    "--fix",
                ]
            )
            self.assertEqual(code, 0)
            self.assertIn("Installed capabilities saved: 2", output)

            code, output = run_cli(
                [
                    "--repo-root",
                    str(root),
                    "--registry",
                    str(registry),
                    "capabilities",
                    "check-installed",
                    "--local-skill-root",
                    str(local_skills),
                ]
            )
            self.assertEqual(code, 0)
            self.assertIn("matching=2", output)
            self.assertIn("missing_in_registry=0", output)

    def test_agent_adapter_turns_npx_timeout_into_failed_result(self):
        with mock.patch("freedom_os_manager.adapters.agents.subprocess.run", side_effect=TimeoutExpired(cmd=["npx"], timeout=30)):
            result = agents.install_skill(Path("/tmp/demo-skill"), ["codex"])

        self.assertEqual(result.returncode, 124)
        self.assertIn("timed out", result.stderr)


def run_cli(argv: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = main(argv)
    return code, stdout.getvalue() + stderr.getvalue()


if __name__ == "__main__":
    unittest.main()
