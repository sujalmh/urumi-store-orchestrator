import json
import logging
import os
import subprocess
from typing import List

logger = logging.getLogger("helm_client")


class HelmClient:
    def install(self, release_name: str, chart_path: str, namespace: str, values_path: str):
        command = [
            "helm",
            "upgrade",
            "--install",
            release_name,
            chart_path,
            "-n",
            namespace,
            "-f",
            values_path,
            "--wait",
            "--timeout",
            "20m",
        ]
        return self._run(command, timeout=1300)

    def uninstall(self, release_name: str, namespace: str):
        command = ["helm", "uninstall", release_name, "-n", namespace]
        return self._run(command, timeout=300)

    def list_releases(self, namespace: str) -> List[dict]:
        command = ["helm", "list", "-n", namespace, "-o", "json"]
        output = self._run(command, timeout=60)
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return []

    @staticmethod
    def _run(command: list[str], timeout: int) -> str:
        import time
        import threading
        cmd_str = ' '.join(command)
        logger.info(f"helm_command_start: {cmd_str}")
        start_time = time.time()
        
        try:
            # Use Popen with DEVNULL for stdout to avoid any pipe buffer issues
            # This is more reliable than subprocess.run for long-running helm --wait commands
            logger.info(f"helm_subprocess_start: spawning process")
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,  # Discard stdout completely
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True  # Create new process group for clean termination
            )
            
            logger.info(f"helm_subprocess_spawned: pid={process.pid}")
            
            # Read stderr in a separate thread to avoid blocking
            stderr_lines = []
            def read_stderr():
                try:
                    if process.stderr:
                        for line in process.stderr:
                            stderr_lines.append(line)
                            if len(stderr_lines) <= 5:  # Log first few lines
                                logger.info(f"helm_stderr: {line.strip()[:200]}")
                except Exception as e:
                    logger.warning(f"stderr_read_error: {e}")
            
            stderr_thread = threading.Thread(target=read_stderr)
            stderr_thread.daemon = True
            stderr_thread.start()
            
            # Wait for process to complete with timeout
            try:
                returncode = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                elapsed = time.time() - start_time
                logger.error(f"helm_command_timeout: elapsed={elapsed:.2f}s, killing pid={process.pid}")
                # Kill the entire process group
                try:
                    import signal
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=5)
                except:
                    process.kill()
                    process.wait()
                raise RuntimeError(f"Helm command timed out after {elapsed:.2f}s")
            
            # Wait for stderr thread to finish
            stderr_thread.join(timeout=5)
            
            elapsed = time.time() - start_time
            stderr_output = ''.join(stderr_lines)
            logger.info(f"helm_subprocess_complete: returncode={returncode}, elapsed={elapsed:.2f}s")
            
            if returncode != 0:
                logger.error(f"helm_command_failed: stderr={stderr_output[:500]}")
                raise RuntimeError(stderr_output.strip() or "Helm command failed")
            
            logger.info(f"helm_command_success: elapsed={elapsed:.2f}s")
            return ""
            
        except RuntimeError:
            raise
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"helm_command_exception: elapsed={elapsed:.2f}s, error={str(e)}")
            raise
