import React from 'react';
import { useFleetStore } from '../../store/useFleetStore';
import { Clock, Info, AlertTriangle, CheckCircle, Activity } from 'lucide-react';

const DispatchPanel: React.FC = () => {
  const lastDispatch = useFleetStore((state) => state.lastDispatch);

  return (
    <div className="bg-white/95 backdrop-blur-md p-4 rounded-xl shadow-2xl border border-blue-100 w-72 transition-all duration-500">
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 bg-blue-100 rounded-lg text-blue-600">
          <Info size={18} />
        </div>
        <h3 className="font-bold text-gray-800 tracking-tight">Dispatch Decision</h3>
      </div>

      {!lastDispatch ? (
        <div className="py-8 flex flex-col items-center justify-center text-gray-400 gap-2 border-2 border-dashed border-gray-100 rounded-lg">
          <Activity size={24} className="animate-pulse" />
          <p className="text-xs font-medium">Waiting for next dispatch...</p>
        </div>
      ) : (
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2">
          {/* Selection Info */}
          <div className="flex items-center justify-between bg-blue-50/50 p-2.5 rounded-lg border border-blue-100/50">
            <div className="flex flex-col">
              <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider">Selected Unit</span>
              <span className="text-lg font-black text-gray-900">{lastDispatch.selected_ambulance}</span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider">Estimated ETA</span>
              <div className="flex items-center gap-1.5 text-blue-700 font-bold">
                <Clock size={14} />
                <span>{lastDispatch.eta}</span>
              </div>
            </div>
          </div>

          {/* Reason */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Selection Rationale</span>
            <p className="text-sm text-gray-700 leading-relaxed font-medium">
              {lastDispatch.reason}
            </p>
          </div>

          {/* Comparison */}
          {lastDispatch.alternatives && lastDispatch.alternatives.length > 0 && (
            <div className="bg-gray-50/80 p-3 rounded-lg border border-gray-100">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle size={12} className="text-orange-500" />
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Alternative Comparison</span>
              </div>
              {lastDispatch.alternatives.map((alt, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-600">Ambulance {alt.id}</span>
                  <span className="text-xs font-bold text-red-500">{alt.eta_diff} slower</span>
                </div>
              ))}
            </div>
          )}

          {/* Traffic Status */}
          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Traffic Analysis</span>
            <div className="flex items-center gap-1 text-green-600 bg-green-50 px-2 py-0.5 rounded-full border border-green-100">
              <CheckCircle size={10} />
              <span className="text-[10px] font-bold">CONSIDERED</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DispatchPanel;
