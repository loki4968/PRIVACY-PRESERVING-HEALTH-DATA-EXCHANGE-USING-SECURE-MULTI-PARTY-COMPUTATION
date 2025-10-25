import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import uuid
from datetime import datetime
import numpy as np
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
import psutil
import os
from pathlib import Path
import hashlib
import pickle
import json
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor system performance and resource usage."""

    def __init__(self):
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "gpu_usage": 0.0,
            "disk_usage": 0.0,
            "network_io": 0.0
        }
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self, interval: float = 1.0):
        """Start performance monitoring."""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Started performance monitoring")

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Stopped performance monitoring")

    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._update_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")

    def _update_metrics(self):
        """Update performance metrics."""
        try:
            # CPU usage
            self.metrics["cpu_usage"] = psutil.cpu_percent(interval=0.1)

            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics["memory_usage"] = memory.percent

            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics["disk_usage"] = disk.percent

            # Network I/O (simplified)
            network = psutil.net_io_counters()
            if network:
                self.metrics["network_io"] = (network.bytes_sent + network.bytes_recv) / 1024 / 1024  # MB

            # GPU usage (if available)
            self.metrics["gpu_usage"] = self._get_gpu_usage()

        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")

    def _get_gpu_usage(self) -> float:
        """Get GPU usage if available."""
        try:
            # Try to use nvidia-ml-py if available
            try:
                from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates
                nvmlInit()
                device_count = nvmlDeviceGetCount()
                if device_count > 0:
                    handle = nvmlDeviceGetHandleByIndex(0)
                    util = nvmlDeviceGetUtilizationRates(handle)
                    return util.gpu
            except ImportError:
                pass

            # Fallback: check for other GPU monitoring tools
            return 0.0

        except Exception:
            return 0.0

    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        return self.metrics.copy()

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            return {
                "cpu_count": mp.cpu_count(),
                "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_total": psutil.disk_usage('/').total,
                "disk_free": psutil.disk_usage('/').free,
                "platform": os.sys.platform,
                "python_version": os.sys.version
            }
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {}

class ModelCache:
    """Cache for trained models and predictions."""

    def __init__(self, cache_dir: str = "cache/", max_cache_size: int = 1000):
        """Initialize the model cache.

        Args:
            cache_dir: Directory to store cached models
            max_cache_size: Maximum number of cached items
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_cache_size = max_cache_size
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, datetime] = {}
        self.cache_lock = threading.Lock()

    def _get_cache_key(self, model_id: str, data_hash: str) -> str:
        """Generate a cache key for model predictions."""
        return f"{model_id}_{data_hash}"

    def _hash_data(self, data: Any) -> str:
        """Generate hash for input data."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    def get(self, model_id: str, data: Any) -> Optional[Any]:
        """Get cached prediction result."""
        cache_key = self._get_cache_key(model_id, self._hash_data(data))

        with self.cache_lock:
            if cache_key in self.cache:
                self.access_times[cache_key] = datetime.now()
                return self.cache[cache_key]

        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    result = pickle.load(f)
                with self.cache_lock:
                    if len(self.cache) < self.max_cache_size:
                        self.cache[cache_key] = result
                        self.access_times[cache_key] = datetime.now()
                return result
            except Exception as e:
                logger.warning(f"Error loading cache file {cache_file}: {str(e)}")

        return None

    def put(self, model_id: str, data: Any, result: Any):
        """Cache prediction result."""
        cache_key = self._get_cache_key(model_id, self._hash_data(data))

        with self.cache_lock:
            # Manage cache size
            if len(self.cache) >= self.max_cache_size:
                # Remove oldest accessed item
                oldest_key = min(self.access_times.keys(), key=self.access_times.get)
                del self.cache[oldest_key]
                del self.access_times[oldest_key]

            # Add to memory cache
            self.cache[cache_key] = result
            self.access_times[cache_key] = datetime.now()

        # Also save to disk
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            logger.warning(f"Error saving cache file {cache_file}: {str(e)}")

    def clear(self):
        """Clear all cached data."""
        with self.cache_lock:
            self.cache.clear()
            self.access_times.clear()

        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Error deleting cache file {cache_file}: {str(e)}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.cache_lock:
            return {
                "memory_cache_size": len(self.cache),
                "max_cache_size": self.max_cache_size,
                "disk_cache_files": len(list(self.cache_dir.glob("*.pkl"))),
                "cache_dir_size": sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl"))
            }

class ParallelProcessor:
    """Handle parallel processing for ML operations."""

    def __init__(self, max_workers: Optional[int] = None):
        """Initialize parallel processor.

        Args:
            max_workers: Maximum number of worker processes/threads
        """
        self.max_workers = max_workers or min(4, mp.cpu_count())
        self.process_executor = ProcessPoolExecutor(max_workers=self.max_workers)
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_workers * 2)

    def shutdown(self):
        """Shutdown executors."""
        self.process_executor.shutdown(wait=True)
        self.thread_executor.shutdown(wait=True)

    def parallel_predict(self, model, data_batches: List[List[Any]], batch_size: int = 100) -> List[Any]:
        """Make predictions in parallel.

        Args:
            model: Trained model
            data_batches: List of data batches
            batch_size: Size of each batch

        Returns:
            predictions: List of predictions
        """
        def predict_batch(batch_data):
            try:
                return model.predict(batch_data)
            except Exception as e:
                logger.error(f"Error in batch prediction: {str(e)}")
                return []

        # Submit all batches for parallel processing
        futures = [
            self.process_executor.submit(predict_batch, batch)
            for batch in data_batches
        ]

        # Collect results
        results = []
        for future in futures:
            try:
                batch_result = future.result(timeout=300)  # 5 minute timeout
                results.extend(batch_result)
            except Exception as e:
                logger.error(f"Error getting batch result: {str(e)}")
                results.append([])

        return results

    def parallel_train(self, train_function, data_chunks: List[Any], **kwargs) -> List[Any]:
        """Train models in parallel on different data chunks.

        Args:
            train_function: Training function to execute
            data_chunks: List of data chunks
            **kwargs: Additional arguments for training function

        Returns:
            results: List of training results
        """
        def train_chunk(chunk_data):
            try:
                return train_function(chunk_data, **kwargs)
            except Exception as e:
                logger.error(f"Error in chunk training: {str(e)}")
                return None

        # Submit all chunks for parallel processing
        futures = [
            self.process_executor.submit(train_chunk, chunk)
            for chunk in data_chunks
        ]

        # Collect results
        results = []
        for future in futures:
            try:
                chunk_result = future.result(timeout=1800)  # 30 minute timeout
                results.append(chunk_result)
            except Exception as e:
                logger.error(f"Error getting chunk result: {str(e)}")
                results.append(None)

        return results

class GPUAccelerator:
    """Handle GPU acceleration for ML operations."""

    def __init__(self):
        self.gpu_available = self._check_gpu_availability()
        self.gpu_memory = 0
        self.gpu_utilization = 0

        if self.gpu_available:
            self._initialize_gpu()

    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        try:
            # Try TensorFlow GPU
            try:
                import tensorflow as tf
                gpus = tf.config.list_physical_devices('GPU')
                if gpus:
                    return True
            except ImportError:
                pass

            # Try PyTorch GPU
            try:
                import torch
                if torch.cuda.is_available():
                    return True
            except ImportError:
                pass

            # Try CuPy
            try:
                import cupy as cp
                return True
            except ImportError:
                pass

            return False

        except Exception:
            return False

    def _initialize_gpu(self):
        """Initialize GPU resources."""
        try:
            if self._check_tensorflow_gpu():
                self._setup_tensorflow_gpu()
            elif self._check_pytorch_gpu():
                self._setup_pytorch_gpu()
            elif self._check_cupy():
                self._setup_cupy()
        except Exception as e:
            logger.warning(f"Error initializing GPU: {str(e)}")
            self.gpu_available = False

    def _check_tensorflow_gpu(self) -> bool:
        try:
            import tensorflow as tf
            return len(tf.config.list_physical_devices('GPU')) > 0
        except ImportError:
            return False

    def _check_pytorch_gpu(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def _check_cupy(self) -> bool:
        try:
            import cupy as cp
            return True
        except ImportError:
            return False

    def _setup_tensorflow_gpu(self):
        """Setup TensorFlow GPU acceleration."""
        try:
            import tensorflow as tf
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info(f"TensorFlow GPU acceleration enabled with {len(gpus)} GPU(s)")
        except Exception as e:
            logger.warning(f"Error setting up TensorFlow GPU: {str(e)}")

    def _setup_pytorch_gpu(self):
        """Setup PyTorch GPU acceleration."""
        try:
            import torch
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                self.gpu_memory = torch.cuda.get_device_properties(0).total_memory
                logger.info(f"PyTorch GPU acceleration enabled with {device_count} GPU(s)")
        except Exception as e:
            logger.warning(f"Error setting up PyTorch GPU: {str(e)}")

    def _setup_cupy(self):
        """Setup CuPy GPU acceleration."""
        try:
            import cupy as cp
            self.gpu_memory = cp.cuda.runtime.getDeviceProperties(0)['totalGlobalMem']
            logger.info("CuPy GPU acceleration enabled")
        except Exception as e:
            logger.warning(f"Error setting up CuPy GPU: {str(e)}")

    def is_available(self) -> bool:
        """Check if GPU acceleration is available."""
        return self.gpu_available

    def get_memory_info(self) -> Dict[str, Any]:
        """Get GPU memory information."""
        if not self.gpu_available:
            return {"available": False}

        try:
            if self._check_pytorch_gpu():
                import torch
                if torch.cuda.is_available():
                    return {
                        "available": True,
                        "total_memory": torch.cuda.get_device_properties(0).total_memory,
                        "allocated_memory": torch.cuda.memory_allocated(0),
                        "cached_memory": torch.cuda.memory_reserved(0)
                    }
            elif self._check_cupy():
                import cupy as cp
                mempool = cp.get_default_memory_pool()
                return {
                    "available": True,
                    "total_memory": self.gpu_memory,
                    "used_memory": mempool.used_bytes(),
                    "total_allocated": mempool.total_bytes()
                }
        except Exception as e:
            logger.error(f"Error getting GPU memory info: {str(e)}")

        return {"available": False}

class MemoryOptimizer:
    """Optimize memory usage for large ML operations."""

    def __init__(self):
        self.memory_efficient_mode = False
        self.chunk_size = 1000
        self.temp_files = []

    def enable_memory_efficient_mode(self, chunk_size: int = 1000):
        """Enable memory-efficient processing."""
        self.memory_efficient_mode = True
        self.chunk_size = chunk_size
        logger.info(f"Enabled memory-efficient mode with chunk size {chunk_size}")

    def disable_memory_efficient_mode(self):
        """Disable memory-efficient processing."""
        self.memory_efficient_mode = False
        logger.info("Disabled memory-efficient mode")

    def process_large_dataset(self, data: np.ndarray, process_function, **kwargs) -> Any:
        """Process large datasets in chunks to manage memory usage.

        Args:
            data: Large dataset to process
            process_function: Function to apply to each chunk
            **kwargs: Additional arguments for process_function

        Returns:
            results: Combined results from all chunks
        """
        if not self.memory_efficient_mode:
            return process_function(data, **kwargs)

        results = []
        n_samples = len(data)

        for i in range(0, n_samples, self.chunk_size):
            chunk = data[i:i + self.chunk_size]
            chunk_result = process_function(chunk, **kwargs)
            results.append(chunk_result)

            # Clean up memory
            del chunk
            if i % (self.chunk_size * 10) == 0:  # Every 10 chunks
                import gc
                gc.collect()

        return self._combine_chunk_results(results)

    def _combine_chunk_results(self, chunk_results: List[Any]) -> Any:
        """Combine results from multiple chunks."""
        if not chunk_results:
            return None

        if isinstance(chunk_results[0], np.ndarray):
            return np.concatenate(chunk_results, axis=0)
        elif isinstance(chunk_results[0], list):
            return [item for chunk in chunk_results for item in chunk]
        else:
            # For other types, try to concatenate or return as list
            try:
                return np.concatenate(chunk_results, axis=0)
            except:
                return chunk_results

    def cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Error removing temp file {temp_file}: {str(e)}")

        self.temp_files.clear()

    def create_temp_file(self, data: Any, suffix: str = "") -> str:
        """Create a temporary file for data storage."""
        import tempfile

        temp_fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix="ml_temp_")
        try:
            with os.fdopen(temp_fd, 'wb') as temp_file:
                pickle.dump(data, temp_file)
            self.temp_files.append(temp_path)
            return temp_path
        except Exception as e:
            os.close(temp_fd)
            logger.error(f"Error creating temp file: {str(e)}")
            raise

class MLPerformanceService:
    """Main service for ML performance optimization."""

    def __init__(self):
        """Initialize the ML performance service."""
        self.performance_monitor = PerformanceMonitor()
        self.model_cache = ModelCache()
        self.parallel_processor = ParallelProcessor()
        self.gpu_accelerator = GPUAccelerator()
        self.memory_optimizer = MemoryOptimizer()

        # Start performance monitoring
        self.performance_monitor.start_monitoring()

        logger.info("Initialized ML Performance Service")

    def shutdown(self):
        """Shutdown the performance service."""
        self.performance_monitor.stop_monitoring()
        self.parallel_processor.shutdown()
        self.memory_optimizer.cleanup_temp_files()
        logger.info("ML Performance Service shutdown complete")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            "system_metrics": self.performance_monitor.get_metrics(),
            "system_info": self.performance_monitor.get_system_info(),
            "cache_stats": self.model_cache.get_cache_stats(),
            "gpu_info": self.gpu_accelerator.get_memory_info(),
            "memory_efficient_mode": self.memory_optimizer.memory_efficient_mode
        }

    def optimize_training(self,
                         X: np.ndarray,
                         y: np.ndarray,
                         train_function,
                         use_gpu: bool = True,
                         use_cache: bool = True,
                         **train_kwargs) -> Dict[str, Any]:
        """Optimize ML model training with performance enhancements.

        Args:
            X: Feature matrix
            y: Target values
            train_function: Training function
            use_gpu: Whether to use GPU acceleration
            use_cache: Whether to use caching
            **train_kwargs: Additional training arguments

        Returns:
            result: Training result with performance metrics
        """
        start_time = time.time()

        try:
            # Check cache first
            if use_cache:
                data_hash = self.model_cache._hash_data({"X": X.tolist(), "y": y.tolist(), **train_kwargs})
                cache_key = f"training_{data_hash}"
                cached_result = self.model_cache.get(cache_key, {"X": X.tolist(), "y": y.tolist()})
                if cached_result:
                    logger.info("Using cached training result")
                    return cached_result

            # Use GPU if available and requested
            if use_gpu and self.gpu_accelerator.is_available():
                logger.info("Using GPU acceleration for training")
                # GPU training would be handled by the specific framework

            # Use memory optimization for large datasets
            if len(X) > 10000:  # Large dataset threshold
                self.memory_optimizer.enable_memory_efficient_mode()
                logger.info("Enabled memory-efficient mode for large dataset")

            # Perform training
            result = train_function(X, y, **train_kwargs)

            # Cache result if requested
            if use_cache:
                self.model_cache.put(cache_key, {"X": X.tolist(), "y": y.tolist()}, result)

            training_time = time.time() - start_time

            # Add performance metrics
            result["performance_metrics"] = {
                "training_time": training_time,
                "dataset_size": len(X),
                "feature_count": X.shape[1] if len(X.shape) > 1 else 1,
                "gpu_used": use_gpu and self.gpu_accelerator.is_available(),
                "memory_efficient": self.memory_optimizer.memory_efficient_mode,
                "cached": use_cache
            }

            logger.info(f"Training completed in {training_time:.2f} seconds")

            return result

        except Exception as e:
            training_time = time.time() - start_time
            logger.error(f"Error in optimized training: {str(e)}")
            return {
                "error": str(e),
                "training_time": training_time,
                "performance_metrics": {
                    "training_time": training_time,
                    "failed": True
                }
            }

    def optimize_prediction(self,
                           model,
                           X: np.ndarray,
                           use_gpu: bool = True,
                           use_cache: bool = True,
                           batch_size: int = 1000) -> Dict[str, Any]:
        """Optimize ML model predictions with performance enhancements.

        Args:
            model: Trained model
            X: Feature matrix
            use_gpu: Whether to use GPU acceleration
            use_cache: Whether to use caching
            batch_size: Batch size for processing

        Returns:
            result: Prediction result with performance metrics
        """
        start_time = time.time()

        try:
            # Check cache first
            if use_cache:
                cached_result = self.model_cache.get(model.model_id if hasattr(model, 'model_id') else str(id(model)), X.tolist())
                if cached_result:
                    logger.info("Using cached prediction result")
                    return cached_result

            # Use GPU if available and requested
            if use_gpu and self.gpu_accelerator.is_available():
                logger.info("Using GPU acceleration for prediction")
                # GPU prediction would be handled by the specific framework

            # Process in batches for large datasets
            if len(X) > batch_size:
                logger.info(f"Processing {len(X)} predictions in batches of {batch_size}")

                # Split data into batches
                batches = [X[i:i + batch_size] for i in range(0, len(X), batch_size)]

                # Use parallel processing for batches
                predictions = self.parallel_processor.parallel_predict(model, batches, batch_size)
                predictions = [pred for batch_pred in predictions for pred in batch_pred]
            else:
                predictions = model.predict(X)

            prediction_time = time.time() - start_time

            result = {
                "predictions": predictions,
                "prediction_count": len(predictions),
                "performance_metrics": {
                    "prediction_time": prediction_time,
                    "predictions_per_second": len(predictions) / prediction_time,
                    "dataset_size": len(X),
                    "batch_size": batch_size,
                    "gpu_used": use_gpu and self.gpu_accelerator.is_available(),
                    "parallel_processing": len(X) > batch_size,
                    "cached": use_cache
                }
            }

            # Cache result if requested
            if use_cache:
                self.model_cache.put(
                    model.model_id if hasattr(model, 'model_id') else str(id(model)),
                    X.tolist(),
                    result
                )

            logger.info(f"Predictions completed in {prediction_time".2f"} seconds ({len(predictions) / prediction_time".0f"} pred/s)")

            return result

        except Exception as e:
            prediction_time = time.time() - start_time
            logger.error(f"Error in optimized prediction: {str(e)}")
            return {
                "error": str(e),
                "prediction_time": prediction_time,
                "performance_metrics": {
                    "prediction_time": prediction_time,
                    "failed": True
                }
            }

    def clear_cache(self):
        """Clear all cached data."""
        self.model_cache.clear()
        logger.info("Cleared all cached data")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.model_cache.get_cache_stats()

    def preload_models(self, model_paths: List[str]):
        """Preload models into cache for faster access.

        Args:
            model_paths: List of paths to model files
        """
        for model_path in model_paths:
            try:
                # Load model (implementation depends on model type)
                # This is a placeholder - actual implementation would depend on model framework
                logger.info(f"Preloading model from {model_path}")
            except Exception as e:
                logger.warning(f"Error preloading model {model_path}: {str(e)}")

    def optimize_hyperparameter_search(self,
                                     X: np.ndarray,
                                     y: np.ndarray,
                                     param_grid: Dict[str, List[Any]],
                                     search_function,
                                     n_jobs: int = -1) -> Dict[str, Any]:
        """Optimize hyperparameter search with parallel processing.

        Args:
            X: Feature matrix
            y: Target values
            param_grid: Parameter grid for search
            search_function: Hyperparameter search function
            n_jobs: Number of parallel jobs (-1 for all available cores)

        Returns:
            result: Search result with performance metrics
        """
        start_time = time.time()

        try:
            # Use all available cores if n_jobs is -1
            if n_jobs == -1:
                n_jobs = mp.cpu_count()

            # Perform parallel hyperparameter search
            result = search_function(X, y, param_grid, n_jobs=n_jobs)

            search_time = time.time() - start_time

            result["performance_metrics"] = {
                "search_time": search_time,
                "parameter_combinations": len(param_grid[list(param_grid.keys())[0]]) if param_grid else 0,
                "parallel_jobs": n_jobs,
                "total_cores": mp.cpu_count()
            }

            logger.info(f"Hyperparameter search completed in {search_time".2f"} seconds")

            return result

        except Exception as e:
            search_time = time.time() - start_time
            logger.error(f"Error in hyperparameter search: {str(e)}")
            return {
                "error": str(e),
                "search_time": search_time,
                "performance_metrics": {
                    "search_time": search_time,
                    "failed": True
                }
            }

# Global instance
ml_performance_service = MLPerformanceService()
