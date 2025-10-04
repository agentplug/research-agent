"""
Parallel executor for concurrent processing of multiple sources.

This module handles the parallel execution of source processing tasks
using ThreadPoolExecutor for improved performance.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List

# Set up logger
logger = logging.getLogger(__name__)


class ParallelExecutor:
    """Executes source processing tasks in parallel."""

    def __init__(self, max_workers: int = 5):
        """
        Initialize parallel executor.

        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers

    def execute_parallel(
        self,
        tasks: List[Dict[str, Any]],
        processor_func: Callable[[Dict[str, Any]], Any],
        task_name: str = "task",
    ) -> List[Any]:
        """
        Execute tasks in parallel using ThreadPoolExecutor.

        Args:
            tasks: List of task data dictionaries
            processor_func: Function to process each task
            task_name: Name of the task type for logging

        Returns:
            List of processed results
        """
        if not tasks:
            return []

        processed_results = []
        start_time = time.time()

        logger.info(
            f"Processing {len(tasks)} {task_name}s in parallel"
        )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(processor_func, task): task for task in tasks
            }

            # Collect results as they complete
            completed_count = 0
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    if result:  # Only add non-None results
                        processed_results.append(result)
                    completed_count += 1
                    logger.info(f"Processing progress: {completed_count}/{len(tasks)} {task_name}s completed")
                except Exception as e:
                    # Log error but continue processing other tasks
                    task = future_to_task[future]
                    logger.error(
                        f"❌ Error processing {task_name} {task.get('tool_name', 'unknown')}: {e}"
                    )
                    completed_count += 1

        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(
            f"Processing result: Completed {len(processed_results)} {task_name}s in {processing_time:.2f}s"
        )

        return processed_results

    def execute_with_progress(
        self,
        tasks: List[Dict[str, Any]],
        processor_func: Callable[[Dict[str, Any]], Any],
        task_name: str = "task",
        progress_callback: Callable[[int, int], None] = None,
    ) -> List[Any]:
        """
        Execute tasks in parallel with custom progress callback.

        Args:
            tasks: List of task data dictionaries
            processor_func: Function to process each task
            task_name: Name of the task type for logging
            progress_callback: Optional callback for progress updates (completed, total)

        Returns:
            List of processed results
        """
        if not tasks:
            return []

        processed_results = []
        start_time = time.time()

        logger.info(
            f"Processing {len(tasks)} {task_name}s in parallel"
        )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(processor_func, task): task for task in tasks
            }

            # Collect results as they complete
            completed_count = 0
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    if result:  # Only add non-None results
                        processed_results.append(result)
                    completed_count += 1

                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(completed_count, len(tasks))
                    else:
                        logger.info(
                            f"✅ Completed {completed_count}/{len(tasks)} {task_name}s"
                        )

                except Exception as e:
                    # Log error but continue processing other tasks
                    task = future_to_task[future]
                    logger.error(
                        f"❌ Error processing {task_name} {task.get('tool_name', 'unknown')}: {e}"
                    )
                    completed_count += 1

        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(
            f"Processing result: Completed {len(processed_results)} {task_name}s in {processing_time:.2f}s"
        )

        return processed_results

    def get_execution_stats(
        self, tasks: List[Dict[str, Any]], results: List[Any]
    ) -> Dict[str, Any]:
        """
        Get execution statistics.

        Args:
            tasks: Original task list
            results: Processed results

        Returns:
            Dictionary containing execution statistics
        """
        return {
            "total_tasks": len(tasks),
            "successful_results": len(results),
            "success_rate": len(results) / len(tasks) if tasks else 0.0,
            "max_workers": self.max_workers,
        }
