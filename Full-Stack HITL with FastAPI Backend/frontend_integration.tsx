/**
 * Frontend Integration Example for HITL Backend
 * React/Next.js components for interacting with FastAPI HITL backend
 */

import { useState, useEffect } from 'react';

// Types
interface CrewRequest {
  message?: string;
  user_input?: string;
  campaign_context?: string;
  language?: string;
  checkpoints?: string[];
}

interface ExecutionStatus {
  execution_id: string;
  status: string;
  current_checkpoint?: string;
  completed_checkpoints: string[];
  result?: any;
  error?: string;
}

interface CheckpointInfo {
  execution_id: string;
  checkpoint_id: string;
  checkpoint_name: string;
  description: string;
  context: Record<string, any>;
  status: string;
  created_at: string;
}

interface FeedbackRequest {
  execution_id: string;
  checkpoint_id: string;
  action: 'continue' | 'stop' | 'revise' | 'skip';
  feedback?: string;
}

// HITL API Client
class HITLClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async executeCrew(request: CrewRequest): Promise<ExecutionStatus> {
    const response = await fetch(`${this.baseUrl}/api/crew/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getStatus(executionId: string): Promise<ExecutionStatus> {
    const response = await fetch(`${this.baseUrl}/api/crew/status/${executionId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async getCheckpoint(executionId: string): Promise<CheckpointInfo> {
    const response = await fetch(`${this.baseUrl}/api/crew/checkpoint/${executionId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }

  async submitFeedback(feedback: FeedbackRequest): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/crew/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feedback),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}

// React Hook for HITL Workflow
export function useHITLWorkflow() {
  const [executionId, setExecutionId] = useState<string | null>(null);
  const [status, setStatus] = useState<ExecutionStatus | null>(null);
  const [checkpoint, setCheckpoint] = useState<CheckpointInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const client = new HITLClient();

  // Poll for status updates
  useEffect(() => {
    if (!executionId) return;

    const pollInterval = setInterval(async () => {
      try {
        const currentStatus = await client.getStatus(executionId);
        setStatus(currentStatus);

        // Check for pending checkpoint
        if (currentStatus.status === 'waiting_feedback') {
          try {
            const checkpointInfo = await client.getCheckpoint(executionId);
            setCheckpoint(checkpointInfo);
          } catch (e) {
            // No checkpoint yet
            setCheckpoint(null);
          }
        } else {
          setCheckpoint(null);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to poll status');
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [executionId]);

  const startExecution = async (request: CrewRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await client.executeCrew(request);
      setExecutionId(result.execution_id);
      setStatus(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start execution');
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (
    checkpointId: string,
    action: 'continue' | 'stop' | 'revise' | 'skip',
    feedback?: string
  ) => {
    if (!executionId) return;

    setLoading(true);
    try {
      await client.submitFeedback({
        execution_id: executionId,
        checkpoint_id: checkpointId,
        action,
        feedback,
      });
      // Status will update via polling
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  };

  return {
    executionId,
    status,
    checkpoint,
    loading,
    error,
    startExecution,
    submitFeedback,
  };
}

// Checkpoint Approval Component
export function CheckpointApproval({
  checkpoint,
  onSubmit,
  loading,
}: {
  checkpoint: CheckpointInfo;
  onSubmit: (action: string, feedback?: string) => void;
  loading: boolean;
}) {
  const [feedback, setFeedback] = useState('');

  return (
    <div className="border rounded-lg p-6 bg-yellow-50">
      <h3 className="text-lg font-semibold mb-2">🔍 Checkpoint: {checkpoint.checkpoint_name}</h3>
      <p className="text-gray-700 mb-4">{checkpoint.description}</p>

      <div className="mb-4">
        <h4 className="font-medium mb-2">Context:</h4>
        <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto max-h-48">
          {JSON.stringify(checkpoint.context, null, 2)}
        </pre>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Feedback (optional, for revise action):
        </label>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          className="w-full p-2 border rounded"
          rows={3}
          placeholder="Enter feedback..."
        />
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => onSubmit('continue')}
          disabled={loading}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
        >
          Continue
        </button>
        <button
          onClick={() => onSubmit('stop')}
          disabled={loading}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
        >
          Stop
        </button>
        <button
          onClick={() => onSubmit('revise', feedback)}
          disabled={loading || !feedback}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          Revise
        </button>
        <button
          onClick={() => onSubmit('skip')}
          disabled={loading}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50"
        >
          Skip
        </button>
      </div>
    </div>
  );
}

// Example Usage Component
export function HITLWorkflowExample() {
  const {
    executionId,
    status,
    checkpoint,
    loading,
    error,
    startExecution,
    submitFeedback,
  } = useHITLWorkflow();

  const handleStart = () => {
    startExecution({
      message: 'Create a content plan for a summer campaign',
      language: 'English',
      checkpoints: ['after_planning', 'after_analysis'],
    });
  };

  const handleFeedback = (action: string, feedback?: string) => {
    if (!checkpoint) return;
    submitFeedback(checkpoint.checkpoint_id, action as any, feedback);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">HITL Workflow Example</h2>

      {!executionId && (
        <button
          onClick={handleStart}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Start Execution
        </button>
      )}

      {error && <div className="text-red-600 mt-4">Error: {error}</div>}

      {status && (
        <div className="mt-4">
          <p>Status: {status.status}</p>
          <p>Execution ID: {executionId}</p>
        </div>
      )}

      {checkpoint && (
        <div className="mt-4">
          <CheckpointApproval
            checkpoint={checkpoint}
            onSubmit={handleFeedback}
            loading={loading}
          />
        </div>
      )}

      {status?.result && (
        <div className="mt-4 p-4 bg-green-50 rounded">
          <h3 className="font-semibold">Result:</h3>
          <pre className="mt-2 text-sm">{JSON.stringify(status.result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
