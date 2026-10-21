import React from "react";
import { Zap, Thermometer } from "lucide-react";

interface MotorTelemetryCardsProps {
  stepperMotorLoad: {
    value: string;
    status: string;
  };
  driverTemperature: {
    value: string;
    status: string;
  };
}

export default function MotorTelemetryCards({
  stepperMotorLoad,
  driverTemperature,
}: MotorTelemetryCardsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
      {/* Stepper Motor Load Card */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-emerald-100/70 text-emerald-800 flex items-center justify-center shrink-0">
          <Zap className="w-5 h-5 fill-emerald-800" />
        </div>
        <div>
          <span className="block text-xs font-medium text-slate-400 mb-0.5">
            Stepper Motor Load
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold text-slate-800">
              {stepperMotorLoad.value}
            </span>
            <span className="text-xs font-semibold text-emerald-700">
              ({stepperMotorLoad.status})
            </span>
          </div>
        </div>
      </div>

      {/* Driver Temperature Card */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-teal-100/70 text-teal-800 flex items-center justify-center shrink-0">
          <Thermometer className="w-5 h-5" />
        </div>
        <div>
          <span className="block text-xs font-medium text-slate-400 mb-0.5">
            Driver Temperature
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold text-slate-800">
              {driverTemperature.value}
            </span>
            <span className="text-xs font-semibold text-emerald-700">
              ({driverTemperature.status})
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
