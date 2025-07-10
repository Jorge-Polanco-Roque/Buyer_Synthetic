"""
Advanced tracing system for Buyer Synthetic™ agents.
Captures structured logs for audit chatbot analysis.
"""

import json
import time
import uuid
import logging
import traceback
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import sqlite3
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class TraceLevel(str, Enum):
    """Trace levels for different types of operations"""
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    NODE_ENTER = "node_enter"
    NODE_EXIT = "node_exit"
    LLM_CALL = "llm_call"
    LLM_RESPONSE = "llm_response"
    DATA_INPUT = "data_input"
    DATA_OUTPUT = "data_output"
    ERROR = "error"
    VALIDATION = "validation"
    DECISION = "decision"
    METRIC = "metric"


@dataclass
class TraceEvent:
    """Structured trace event for agent operations"""
    
    # Basic identification
    trace_id: str
    event_id: str
    timestamp: str
    level: TraceLevel
    
    # Agent context
    agent_name: str
    operation: str
    agent_version: str = "1.0.0"
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Operation details
    node_name: Optional[str] = None
    step_number: int = 0
    
    # Data payload
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Performance metrics
    duration_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    # Error handling
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # LLM specific
    model_name: Optional[str] = None
    prompt: Optional[str] = None
    response: Optional[str] = None
    tokens_used: Optional[int] = None
    
    # Validation results
    validation_passed: Optional[bool] = None
    validation_score: Optional[float] = None
    validation_details: Optional[Dict[str, Any]] = None


class AgentTracer:
    """
    Centralized tracing system for all agent operations.
    Stores structured logs that can be queried by the audit chatbot.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize tracer with database backend"""
        if db_path:
            self.db_path = db_path
        else:
            # Create organized folder structure
            base_dir = Path("data/audit_traces")
            today = datetime.now().strftime("%Y-%m-%d")
            self.traces_dir = base_dir / today
            self.traces_dir.mkdir(parents=True, exist_ok=True)
            
            # Database file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.db_path = str(self.traces_dir / f"traces_{timestamp}.db")
        
        self.current_traces: Dict[str, TraceEvent] = {}
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for traces"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    event_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    agent_version TEXT DEFAULT '1.0.0',
                    session_id TEXT,
                    user_id TEXT,
                    operation TEXT NOT NULL,
                    node_name TEXT,
                    step_number INTEGER DEFAULT 0,
                    inputs TEXT,  -- JSON
                    outputs TEXT,  -- JSON
                    metadata TEXT,  -- JSON
                    duration_ms REAL,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL,
                    error_message TEXT,
                    error_type TEXT,
                    stack_trace TEXT,
                    model_name TEXT,
                    prompt TEXT,
                    response TEXT,
                    tokens_used INTEGER,
                    validation_passed BOOLEAN,
                    validation_score REAL,
                    validation_details TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trace_id ON traces(trace_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON traces(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_name ON traces(agent_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_level ON traces(level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON traces(session_id)")
    
    def start_trace(self, 
                   agent_name: str,
                   operation: str,
                   session_id: Optional[str] = None,
                   user_id: Optional[str] = None,
                   inputs: Optional[Dict[str, Any]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new trace for an agent operation"""
        
        trace_id = str(uuid.uuid4())
        event_id = f"{trace_id}_start"
        
        trace_event = TraceEvent(
            trace_id=trace_id,
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=TraceLevel.AGENT_START,
            agent_name=agent_name,
            operation=operation,
            session_id=session_id,
            user_id=user_id,
            inputs=inputs,
            metadata=metadata
        )
        
        with self._lock:
            self.current_traces[trace_id] = trace_event
        
        self._store_event(trace_event)
        
        logger.info(f"Started trace {trace_id} for {agent_name}:{operation}")
        return trace_id
    
    def end_trace(self, 
                  trace_id: str,
                  outputs: Optional[Dict[str, Any]] = None,
                  duration_ms: Optional[float] = None,
                  error: Optional[Exception] = None) -> None:
        """End a trace with final outputs and metrics"""
        
        event_id = f"{trace_id}_end"
        
        # Get original trace info
        original_trace = self.current_traces.get(trace_id)
        if not original_trace:
            logger.warning(f"No active trace found for {trace_id}")
            return
        
        trace_event = TraceEvent(
            trace_id=trace_id,
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=TraceLevel.AGENT_END,
            agent_name=original_trace.agent_name,
            operation=original_trace.operation,
            session_id=original_trace.session_id,
            user_id=original_trace.user_id,
            outputs=outputs,
            duration_ms=duration_ms,
            error_message=str(error) if error else None,
            error_type=type(error).__name__ if error else None
        )
        
        with self._lock:
            if trace_id in self.current_traces:
                del self.current_traces[trace_id]
        
        self._store_event(trace_event)
        
        status = "with error" if error else "successfully"
        logger.info(f"Ended trace {trace_id} {status}")
    
    def log_node_entry(self,
                      trace_id: str,
                      node_name: str,
                      step_number: int = 0,
                      inputs: Optional[Dict[str, Any]] = None) -> None:
        """Log entry into a LangGraph node"""
        
        event_id = f"{trace_id}_node_{node_name}_{step_number}_enter"
        
        original_trace = self.current_traces.get(trace_id)
        if not original_trace:
            logger.warning(f"No active trace found for {trace_id}")
            return
        
        trace_event = TraceEvent(
            trace_id=trace_id,
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=TraceLevel.NODE_ENTER,
            agent_name=original_trace.agent_name,
            operation=original_trace.operation,
            session_id=original_trace.session_id,
            node_name=node_name,
            step_number=step_number,
            inputs=inputs
        )
        
        self._store_event(trace_event)
        logger.debug(f"Node entry: {node_name} (step {step_number})")
    
    def log_node_exit(self,
                     trace_id: str,
                     node_name: str,
                     step_number: int = 0,
                     outputs: Optional[Dict[str, Any]] = None,
                     duration_ms: Optional[float] = None) -> None:
        """Log exit from a LangGraph node"""
        
        event_id = f"{trace_id}_node_{node_name}_{step_number}_exit"
        
        original_trace = self.current_traces.get(trace_id)
        if not original_trace:
            logger.warning(f"No active trace found for {trace_id}")
            return
        
        trace_event = TraceEvent(
            trace_id=trace_id,
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=TraceLevel.NODE_EXIT,
            agent_name=original_trace.agent_name,
            operation=original_trace.operation,
            session_id=original_trace.session_id,
            node_name=node_name,
            step_number=step_number,
            outputs=outputs,
            duration_ms=duration_ms
        )
        
        self._store_event(trace_event)
        logger.debug(f"Node exit: {node_name} (step {step_number}) - {duration_ms}ms")
    
    def log_llm_call(self,
                    trace_id: str,
                    model_name: str,
                    prompt: str,
                    node_name: Optional[str] = None) -> str:
        """Log LLM call with prompt"""
        
        call_id = str(uuid.uuid4())
        event_id = f"{trace_id}_llm_{call_id}_call"
        
        original_trace = self.current_traces.get(trace_id)
        if not original_trace:
            logger.warning(f"No active trace found for {trace_id}")
            return call_id
        
        trace_event = TraceEvent(
            trace_id=trace_id,
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=TraceLevel.LLM_CALL,
            agent_name=original_trace.agent_name,
            operation=original_trace.operation,
            session_id=original_trace.session_id,
            node_name=node_name,
            model_name=model_name,
            prompt=prompt
        )
        
        self._store_event(trace_event)
        logger.debug(f"LLM call: {model_name} - {len(prompt)} chars")
        return call_id
    
    def log_llm_response(self,
                        trace_id: str,
                        call_id: str,
                        response: str,
                        tokens_used: Optional[int] = None,
                        duration_ms: Optional[float] = None) -> None:
        """Log LLM response"""
        
        event_id = f"{trace_id}_llm_{call_id}_response"
        
        original_trace = self.current_traces.get(trace_id)
        if not original_trace:
            logger.warning(f"No active trace found for {trace_id}")
            return
        
        trace_event = TraceEvent(
            trace_id=trace_id,
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=TraceLevel.LLM_RESPONSE,
            agent_name=original_trace.agent_name,
            operation=original_trace.operation,
            session_id=original_trace.session_id,
            response=response,
            tokens_used=tokens_used,
            duration_ms=duration_ms
        )
        
        self._store_event(trace_event)
        logger.debug(f"LLM response: {len(response)} chars, {tokens_used} tokens, {duration_ms}ms")
    
    def log_validation(self,
                      trace_id: str,
                      validation_passed: bool,
                      validation_score: Optional[float] = None,
                      validation_details: Optional[Dict[str, Any]] = None,
                      node_name: Optional[str] = None) -> None:
        """Log validation results"""
        
        event_id = f"{trace_id}_validation_{uuid.uuid4()}"
        
        original_trace = self.current_traces.get(trace_id)
        if not original_trace:
            logger.warning(f"No active trace found for {trace_id}")
            return
        
        trace_event = TraceEvent(
            trace_id=trace_id,
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=TraceLevel.VALIDATION,
            agent_name=original_trace.agent_name,
            operation=original_trace.operation,
            session_id=original_trace.session_id,
            node_name=node_name,
            validation_passed=validation_passed,
            validation_score=validation_score,
            validation_details=validation_details
        )
        
        self._store_event(trace_event)
        status = "PASSED" if validation_passed else "FAILED"
        logger.info(f"Validation {status}: score={validation_score}")
    
    def log_error(self,
                 trace_id: str,
                 error: Exception,
                 node_name: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None) -> None:
        """Log error occurrence"""
        
        import traceback
        
        event_id = f"{trace_id}_error_{uuid.uuid4()}"
        
        original_trace = self.current_traces.get(trace_id)
        if not original_trace:
            logger.warning(f"No active trace found for {trace_id}")
            return
        
        trace_event = TraceEvent(
            trace_id=trace_id,
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=TraceLevel.ERROR,
            agent_name=original_trace.agent_name,
            operation=original_trace.operation,
            session_id=original_trace.session_id,
            node_name=node_name,
            error_message=str(error),
            error_type=type(error).__name__,
            stack_trace=traceback.format_exc(),
            metadata=context
        )
        
        self._store_event(trace_event)
        logger.error(f"Error in {node_name or 'unknown'}: {error}")
    
    def _store_event(self, event: TraceEvent) -> None:
        """Store trace event in database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO traces (
                        trace_id, event_id, timestamp, level, agent_name, agent_version,
                        session_id, user_id, operation, node_name, step_number,
                        inputs, outputs, metadata, duration_ms, memory_usage_mb, cpu_usage_percent,
                        error_message, error_type, stack_trace, model_name, prompt, response,
                        tokens_used, validation_passed, validation_score, validation_details
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.trace_id, event.event_id, event.timestamp, event.level.value,
                    event.agent_name, event.agent_version, event.session_id, event.user_id,
                    event.operation, event.node_name, event.step_number,
                    json.dumps(event.inputs) if event.inputs else None,
                    json.dumps(event.outputs) if event.outputs else None,
                    json.dumps(event.metadata) if event.metadata else None,
                    event.duration_ms, event.memory_usage_mb, event.cpu_usage_percent,
                    event.error_message, event.error_type, event.stack_trace,
                    event.model_name, event.prompt, event.response, event.tokens_used,
                    event.validation_passed, event.validation_score,
                    json.dumps(event.validation_details) if event.validation_details else None
                ))
        except Exception as e:
            logger.error(f"Failed to store trace event: {e}")
    
    @contextmanager
    def trace_node(self, 
                   trace_id: str,
                   node_name: str,
                   step_number: int = 0,
                   inputs: Optional[Dict[str, Any]] = None):
        """Context manager for tracing node execution"""
        
        start_time = time.time()
        
        try:
            self.log_node_entry(trace_id, node_name, step_number, inputs)
            yield
        except Exception as e:
            self.log_error(trace_id, e, node_name)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.log_node_exit(trace_id, node_name, step_number, duration_ms=duration_ms)
    
    def query_traces(self,
                    trace_id: Optional[str] = None,
                    agent_name: Optional[str] = None,
                    operation: Optional[str] = None,
                    level: Optional[TraceLevel] = None,
                    session_id: Optional[str] = None,
                    start_time: Optional[str] = None,
                    end_time: Optional[str] = None,
                    limit: int = 1000) -> List[Dict[str, Any]]:
        """Query traces with filters for the audit chatbot"""
        
        query = "SELECT * FROM traces WHERE 1=1"
        params = []
        
        if trace_id:
            query += " AND trace_id = ?"
            params.append(trace_id)
        
        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)
        
        if operation:
            query += " AND operation = ?"
            params.append(operation)
        
        if level:
            query += " AND level = ?"
            params.append(level.value)
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to query traces: {e}")
            return []
    
    def get_all_traces(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get all traces from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM traces 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get all traces: {e}")
            return []
    
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """Get comprehensive summary of a trace for chatbot context"""
        
        traces = self.query_traces(trace_id=trace_id)
        if not traces:
            return {}
        
        summary = {
            "trace_id": trace_id,
            "agent_name": traces[0]["agent_name"],
            "operation": traces[0]["operation"],
            "session_id": traces[0]["session_id"],
            "start_time": None,
            "end_time": None,
            "total_duration_ms": 0,
            "total_tokens_used": 0,
            "nodes_executed": [],
            "llm_calls": 0,
            "validations": [],
            "errors": [],
            "inputs": None,
            "outputs": None
        }
        
        for trace in traces:
            level = trace["level"]
            
            if level == "agent_start":
                summary["start_time"] = trace["timestamp"]
                if trace["inputs"]:
                    summary["inputs"] = json.loads(trace["inputs"])
            
            elif level == "agent_end":
                summary["end_time"] = trace["timestamp"]
                if trace["outputs"]:
                    summary["outputs"] = json.loads(trace["outputs"])
                if trace["duration_ms"]:
                    summary["total_duration_ms"] = trace["duration_ms"]
            
            elif level == "node_enter":
                if trace["node_name"] not in summary["nodes_executed"]:
                    summary["nodes_executed"].append(trace["node_name"])
            
            elif level == "llm_response":
                summary["llm_calls"] += 1
                if trace["tokens_used"]:
                    summary["total_tokens_used"] += trace["tokens_used"]
            
            elif level == "validation":
                summary["validations"].append({
                    "node": trace["node_name"],
                    "passed": trace["validation_passed"],
                    "score": trace["validation_score"],
                    "details": json.loads(trace["validation_details"]) if trace["validation_details"] else None
                })
            
            elif level == "error":
                summary["errors"].append({
                    "node": trace["node_name"],
                    "type": trace["error_type"],
                    "message": trace["error_message"]
                })
        
        return summary
    
    def export_trace_summary(self, trace_id: str) -> Optional[Dict]:
        """Export comprehensive summary for a specific trace"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all events for this trace
            cursor.execute("""
                SELECT * FROM traces 
                WHERE trace_id = ? 
                ORDER BY timestamp
            """, (trace_id,))
            
            events = [dict(row) for row in cursor.fetchall()]
            
            if not events:
                return None
            
            summary = {
                "trace_id": trace_id,
                "agent_name": events[0]["agent_name"],
                "operation": events[0]["operation"],
                "start_time": events[0]["timestamp"],
                "end_time": events[-1]["timestamp"],
                "total_events": len(events),
                "duration_ms": sum(e.get("duration_ms", 0) for e in events if e.get("duration_ms")),
                "success": all(e.get("error_message") is None for e in events),
                "events": events,
                "summary": {
                    "llm_calls": len([e for e in events if e["level"] == "llm_call"]),
                    "node_entries": len([e for e in events if e["level"] == "node_enter"]),
                    "errors": [e for e in events if e["level"] == "error"],
                    "validations": [e for e in events if e["level"] == "validation"]
                }
            }
            
            return summary
    
    def export_session_summary(self, session_id: str, output_path: Optional[str] = None) -> str:
        """Export complete session summary to JSON file"""
        session_traces = self.get_session_traces(session_id)
        
        if not session_traces:
            logger.warning(f"No traces found for session {session_id}")
            return ""
        
        # Organize by trace_id
        traces_by_id = {}
        for trace in session_traces:
            trace_id = trace["trace_id"]
            if trace_id not in traces_by_id:
                traces_by_id[trace_id] = []
            traces_by_id[trace_id].append(trace)
        
        # Create comprehensive summary
        session_summary = {
            "session_id": session_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_traces": len(traces_by_id),
            "total_events": len(session_traces),
            "traces": {}
        }
        
        for trace_id, events in traces_by_id.items():
            session_summary["traces"][trace_id] = self.export_trace_summary(trace_id)
        
        # Save to file
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.traces_dir / f"session_{session_id}_{timestamp}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(session_summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Session summary exported to {output_path}")
        return output_path
    
    def get_session_traces(self, session_id: str) -> List[Dict]:
        """Get all traces for a specific session"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM traces 
                WHERE session_id = ? 
                ORDER BY timestamp
            """, (session_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_traces(self, days_to_keep: int = 7) -> int:
        """Clean up traces older than specified days"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        cutoff_iso = cutoff_date.isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count records to be deleted
            cursor.execute("SELECT COUNT(*) FROM traces WHERE timestamp < ?", (cutoff_iso,))
            count = cursor.fetchone()[0]
            
            # Delete old records
            cursor.execute("DELETE FROM traces WHERE timestamp < ?", (cutoff_iso,))
            
            logger.info(f"Cleaned up {count} old trace records")
            return count
    
    def get_trace_statistics(self) -> Dict:
        """Get comprehensive statistics about stored traces"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total counts
            cursor.execute("SELECT COUNT(*) FROM traces")
            stats["total_events"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT trace_id) FROM traces")
            stats["total_traces"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT session_id) FROM traces WHERE session_id IS NOT NULL")
            stats["total_sessions"] = cursor.fetchone()[0]
            
            # By agent
            cursor.execute("SELECT agent_name, COUNT(*) FROM traces GROUP BY agent_name")
            stats["by_agent"] = dict(cursor.fetchall())
            
            # By level
            cursor.execute("SELECT level, COUNT(*) FROM traces GROUP BY level")
            stats["by_level"] = dict(cursor.fetchall())
            
            # Errors
            cursor.execute("SELECT COUNT(*) FROM traces WHERE error_message IS NOT NULL")
            stats["total_errors"] = cursor.fetchone()[0]
            
            # Date range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM traces")
            date_range = cursor.fetchone()
            stats["date_range"] = {
                "earliest": date_range[0],
                "latest": date_range[1]
            }
            
            return stats


# Global tracer instance
_tracer = None

def get_tracer() -> AgentTracer:
    """Get global tracer instance"""
    global _tracer
    if _tracer is None:
        _tracer = AgentTracer()
    return _tracer


def trace_agent_execution(agent_name: str, operation: str):
    """Decorator for tracing agent execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            
            # Extract relevant inputs
            inputs = {
                "args": str(args)[:500],  # Truncate long inputs
                "kwargs_keys": list(kwargs.keys())
            }
            
            trace_id = tracer.start_trace(
                agent_name=agent_name,
                operation=operation,
                inputs=inputs
            )
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                outputs = {
                    "result_type": type(result).__name__,
                    "result_preview": str(result)[:500] if result else None
                }
                
                duration_ms = (time.time() - start_time) * 1000
                tracer.end_trace(trace_id, outputs=outputs, duration_ms=duration_ms)
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                tracer.end_trace(trace_id, duration_ms=duration_ms, error=e)
                raise
        
        return wrapper
    return decorator