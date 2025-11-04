import { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';

const NotificationContext = createContext();

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider');
  }
  return context;
};

export function NotificationProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const [confirmDialog, setConfirmDialog] = useState(null);

  const showToast = useCallback((message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(toast => toast.id !== id));
    }, 4000);
  }, []);

  const showConfirm = useCallback((message, onConfirm) => {
    return new Promise((resolve) => {
      setConfirmDialog({
        message,
        onConfirm: () => {
          onConfirm?.();
          setConfirmDialog(null);
          resolve(true);
        },
        onCancel: () => {
          setConfirmDialog(null);
          resolve(false);
        }
      });
    });
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  return (
    <NotificationContext.Provider value={{ showToast, showConfirm }}>
      {children}

      {/* Toast Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map(toast => (
          <Toast key={toast.id} {...toast} onClose={() => removeToast(toast.id)} />
        ))}
      </div>

      {/* Confirmation Dialog */}
      {confirmDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-dark-card rounded-lg p-6 max-w-md w-full border border-dark-border">
            <h3 className="text-lg font-semibold mb-4">Confirm Action</h3>
            <p className="text-dark-muted mb-6">{confirmDialog.message}</p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={confirmDialog.onCancel}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={confirmDialog.onConfirm}
                className="btn-danger"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </NotificationContext.Provider>
  );
}

function Toast({ id, message, type, onClose }) {
  const icons = {
    success: <CheckCircle className="w-5 h-5 text-accent-success" />,
    error: <XCircle className="w-5 h-5 text-accent-danger" />,
    warning: <AlertCircle className="w-5 h-5 text-accent-warning" />,
    info: <Info className="w-5 h-5 text-accent-primary" />
  };

  const bgColors = {
    success: 'bg-accent-success/10 border-accent-success',
    error: 'bg-accent-danger/10 border-accent-danger',
    warning: 'bg-accent-warning/10 border-accent-warning',
    info: 'bg-accent-primary/10 border-accent-primary'
  };

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-lg border ${bgColors[type]} min-w-[300px] max-w-md shadow-lg animate-slide-in`}
    >
      {icons[type]}
      <p className="flex-1 text-sm">{message}</p>
      <button
        onClick={onClose}
        className="text-dark-muted hover:text-dark-text transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
