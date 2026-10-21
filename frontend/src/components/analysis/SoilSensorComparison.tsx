"use client";

import React, { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, LoaderCircle, Scale } from "lucide-react";
import {
  calculateNpkDose,
  getNpkConfig,
  getNpkSensorDemo,
  type NpkCalculationResponse,
  type NpkConfig,
  type NpkLiquid,
  type NpkRequest,
  type NpkSensorDemo,
} from "@/services/npkApi";

const nutrientRows = [
  { key: "N", label: "Nitrogen (N)", sensorKey: "n_mgkg" },
  { key: "P2O5", label: "Phosphorus (P₂O₅)", sensorKey: "p_mgkg" },
  { key: "K2O", label: "Potassium (K₂O)", sensorKey: "k_mgkg" },
] as const;

function NumberField({
  label,
  value,
  onChange,
  step = "any",
  min = "0",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  step?: string;
  min?: string;
}) {
  return (
    <label className="block text-xs font-semibold text-slate-600">
      {label}
      <input
        type="number"
        min={min}
        step={step}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 font-mono text-sm text-slate-800 outline-none transition focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"
      />
    </label>
  );
}

export default function SoilSensorComparison() {
  const [config, setConfig] = useState<NpkConfig | null>(null);
  const [sensor, setSensor] = useState<NpkSensorDemo | null>(null);
  const [liquid, setLiquid] = useState<NpkLiquid | null>(null);
  const [result, setResult] = useState<NpkCalculationResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [mode, setMode] = useState<NpkRequest["calculation_mode"]>("experimental_soil");
  const [area, setArea] = useState("10");
  const [plants, setPlants] = useState("20");
  const [stageWeek, setStageWeek] = useState<NpkRequest["plot"]["stage_week"]>(4);
  const [calibration, setCalibration] = useState(["", "", ""]);

  useEffect(() => {
    let active = true;
    Promise.all([getNpkConfig(), getNpkSensorDemo()])
      .then(([apiConfig, sensorDemo]) => {
        if (!active) return;
        setConfig(apiConfig);
        setSensor(sensorDemo);
        setLiquid(apiConfig.demo.liquid);
        setArea(String(apiConfig.demo.plot.area));
        setPlants(String(apiConfig.demo.plot.plants));
        setStageWeek(apiConfig.demo.plot.stage_week);
        setLoading(false);
      })
      .catch((reason: unknown) => {
        if (!active) return;
        setError(
          reason instanceof Error ? reason.message : "Could not load the NPK model."
        );
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const runCalculation = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!config || !sensor) return;

    const parsedArea = Number(area);
    const parsedPlants = Number(plants);
    if (!Number.isFinite(parsedArea) || parsedArea <= 0) {
      setError("Plot area must be a positive number.");
      return;
    }
    if (!Number.isInteger(parsedPlants) || parsedPlants <= 0) {
      setError("Plant count must be a positive whole number.");
      return;
    }

    const coefficients = calibration.map((value) =>
      value.trim() === "" ? null : Number(value)
    );
    if (coefficients.some((value) => value !== null && (!Number.isFinite(value) || value < 0))) {
      setError("Calibration coefficients must be zero or greater.");
      return;
    }

    const request: NpkRequest = {
      ...config.demo,
      plot: {
        ...config.demo.plot,
        area: parsedArea,
        plants: parsedPlants,
        stage_week: stageWeek,
      },
      soil: {
        n_mgkg: sensor.n_mgkg,
        p_mgkg: sensor.p_mgkg,
        k_mgkg: sensor.k_mgkg,
        ph: sensor.ph,
        origin: sensor.origin,
      },
      liquid: liquid ?? config.demo.liquid,
      calculation_mode: mode,
      calibration: {
        n_kg_ha_per_mgkg: coefficients[0],
        p2o5_kg_ha_per_mgkg: coefficients[1],
        k2o_kg_ha_per_mgkg: coefficients[2],
        provenance: coefficients.every((value) => value === null)
          ? ""
          : "Entered in the frontend; not agronomically validated",
      },
    };

    setCalculating(true);
    setError("");
    try {
      setResult(await calculateNpkDose(request));
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "NPK calculation failed."
      );
    } finally {
      setCalculating(false);
    }
  };

  const updateSensor = (
    key: "n_mgkg" | "p_mgkg" | "k_mgkg",
    value: string
  ) => {
    if (!sensor) return;
    const parsed = Number(value);
    setSensor({
      ...sensor,
      [key]: Number.isFinite(parsed) ? parsed : 0,
      origin: "MANUAL_UNVERIFIED",
    });
  };

  const formatValue = (value: number | null | undefined, suffix = "") =>
    value == null ? "—" : `${value.toFixed(2)}${suffix}`;

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs md:p-7">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs font-bold uppercase tracking-wider text-teal-800">
            MODEL 2 • SOIL SENSOR VS. DEFICIENCY
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-teal-200 bg-teal-100 px-3 py-1 text-xs font-semibold text-teal-800">
            <Scale className="h-3.5 w-3.5" />
            Electrochemical calibration model
          </span>
        </div>
        <h2 className="mb-1 text-lg font-bold text-slate-800 md:text-xl">
          Soil Sensor vs. NPK Deficiency Comparator
        </h2>
        <p className="max-w-3xl text-xs text-slate-500">
          Live model calculations compare the DOA chilli fertilizer baseline
          with an optional, operator-calibrated soil contribution. The soil
          conversion coefficients are not validated agronomic recommendations.
        </p>
        {sensor && (
          <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2 rounded-xl border border-slate-100 bg-slate-50 p-3 text-xs font-medium text-slate-600">
            <span>
              Sensor source:{" "}
              <span className="font-bold text-amber-700">
                {sensor.origin === "SIMULATED"
                  ? "SIMULATED demo values"
                  : "Unverified manual values"}
              </span>
            </span>
            <span>
              Soil pH:{" "}
              <span className="font-mono font-bold text-slate-800">
                {sensor.ph ?? "—"}
              </span>
            </span>
            <span>Readings are not coming from physical hardware.</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <form
          onSubmit={runCalculation}
          className="space-y-5 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs lg:col-span-1"
        >
          <div>
            <h3 className="text-sm font-bold text-slate-800">Model inputs</h3>
            <p className="mt-1 text-xs text-slate-500">
              Edit soil readings, plot details, and calibration values.
            </p>
          </div>

          {loading ? (
            <div className="flex items-center gap-2 py-5 text-xs text-slate-500">
              <LoaderCircle className="h-4 w-4 animate-spin" />
              Connecting to NPK backend…
            </div>
          ) : (
            <>
              {sensor && (
                <div className="grid grid-cols-3 gap-3">
                  {nutrientRows.map((row) => (
                    <NumberField
                      key={row.sensorKey}
                      label={`${row.key} mg/kg`}
                      value={String(sensor[row.sensorKey])}
                      onChange={(value) => updateSensor(row.sensorKey, value)}
                    />
                  ))}
                </div>
              )}

              <div className="grid grid-cols-2 gap-3">
                <NumberField label="Plot area (m²)" value={area} onChange={setArea} />
                <NumberField
                  label="Plant count"
                  value={plants}
                  onChange={setPlants}
                  step="1"
                  min="1"
                />
              </div>

              {liquid && (
                <fieldset className="space-y-3 rounded-xl border border-slate-200 bg-slate-50/70 p-3">
                  <legend className="px-1 text-xs font-bold text-slate-700">
                    Liquid product label (N–P₂O₅–K₂O)
                  </legend>
                  <p className="text-[11px] leading-relaxed text-slate-500">
                    Mass percentages and density. Values initially come from the
                    backend demo; use the product label for a real comparison.
                  </p>
                  <div className="grid grid-cols-3 gap-2">
                    <NumberField
                      label="N %"
                      value={String(liquid.label_n_percent)}
                      onChange={(value) =>
                        setLiquid({ ...liquid, label_n_percent: Number(value) || 0 })
                      }
                    />
                    <NumberField
                      label="P₂O₅ %"
                      value={String(liquid.label_p2o5_percent)}
                      onChange={(value) =>
                        setLiquid({ ...liquid, label_p2o5_percent: Number(value) || 0 })
                      }
                    />
                    <NumberField
                      label="K₂O %"
                      value={String(liquid.label_k2o_percent)}
                      onChange={(value) =>
                        setLiquid({ ...liquid, label_k2o_percent: Number(value) || 0 })
                      }
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <NumberField
                      label="Density (g/ml)"
                      value={String(liquid.density_g_ml)}
                      onChange={(value) =>
                        setLiquid({ ...liquid, density_g_ml: Number(value) || 0 })
                      }
                      min="0.01"
                    />
                    <NumberField
                      label="Dilution factor"
                      value={String(liquid.dilution_factor)}
                      onChange={(value) =>
                        setLiquid({ ...liquid, dilution_factor: Number(value) || 0 })
                      }
                      min="1"
                    />
                  </div>
                </fieldset>
              )}

              <label className="block text-xs font-semibold text-slate-600">
                Crop stage week
                <select
                  value={stageWeek}
                  onChange={(event) =>
                    setStageWeek(Number(event.target.value) as NpkRequest["plot"]["stage_week"])
                  }
                  className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"
                >
                  {[0, 2, 4, 8, 12, 16].map((week) => (
                    <option key={week} value={week}>
                      Week {week}
                    </option>
                  ))}
                </select>
              </label>

              <label className="block text-xs font-semibold text-slate-600">
                Calculation mode
                <select
                  value={mode}
                  onChange={(event) =>
                    setMode(event.target.value as NpkRequest["calculation_mode"])
                  }
                  className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"
                >
                  <option value="experimental_soil">Experimental soil calibration</option>
                  <option value="reference">DOA reference schedule only</option>
                </select>
              </label>

              {mode === "experimental_soil" && (
                <fieldset className="space-y-3 rounded-xl border border-amber-200 bg-amber-50/60 p-3">
                  <legend className="px-1 text-xs font-bold text-amber-900">
                    Optional soil transfer coefficients
                  </legend>
                  <p className="text-[11px] leading-relaxed text-amber-800">
                    kg/ha per mg/kg. Leave blank until coefficients have been
                    validated for your soil and probe.
                  </p>
                  <div className="grid grid-cols-3 gap-2">
                    {[
                      ["N", 0],
                      ["P₂O₅", 1],
                      ["K₂O", 2],
                    ].map(([label, index]) => (
                      <NumberField
                        key={String(label)}
                        label={String(label)}
                        value={calibration[Number(index)]}
                        onChange={(value) =>
                          setCalibration((current) =>
                            current.map((item, itemIndex) =>
                              itemIndex === Number(index) ? value : item
                            )
                          )
                        }
                      />
                    ))}
                  </div>
                </fieldset>
              )}

              <button
                type="submit"
                disabled={calculating || loading || !config || !sensor || !liquid}
                className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#0f5132] px-4 py-2.5 text-xs font-semibold text-white shadow-xs transition hover:bg-emerald-900 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {calculating ? (
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                ) : (
                  <Scale className="h-4 w-4" />
                )}
                {calculating ? "Calculating…" : "Calculate with NPK model"}
              </button>
            </>
          )}
        </form>

        <section className="space-y-5 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs lg:col-span-2">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-slate-800">Backend calculation</h3>
              <p className="mt-1 text-xs text-slate-500">
                Model results are returned by the NPK_Mix_Model API.
              </p>
            </div>
            {result && (
              <span className="rounded-full bg-teal-50 px-3 py-1 text-[11px] font-bold text-teal-800">
                {result.status.replace(/_/g, " ")}
              </span>
            )}
          </div>

          {error && (
            <div
              role="alert"
              className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-800"
            >
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {result && (
            <>
              {result.modelled.stage_target_nutrient_g_plot ? (
                <>
                  <div className="overflow-x-auto rounded-xl border border-slate-100">
                    <table className="w-full min-w-[620px] text-left text-xs">
                      <thead className="bg-slate-50 text-[10px] uppercase tracking-wider text-slate-500">
                        <tr>
                          <th className="px-3 py-3">Nutrient basis</th>
                          <th className="px-3 py-3">Soil value</th>
                          <th className="px-3 py-3">Estimated soil contribution</th>
                          <th className="px-3 py-3">Remaining season need</th>
                          <th className="px-3 py-3">Modelled stage target</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 text-slate-700">
                        {nutrientRows.map((row) => (
                          <tr key={row.key}>
                            <td className="px-3 py-3 font-bold text-slate-800">{row.label}</td>
                            <td className="px-3 py-3 font-mono">
                              {formatValue(sensor?.[row.sensorKey])} mg/kg
                            </td>
                            <td className="px-3 py-3 font-mono">
                              {formatValue(
                                result.modelled.estimated_soil_contribution_kg_ha?.[row.key]
                              )}{" "}
                              kg/ha
                            </td>
                            <td className="px-3 py-3 font-mono">
                              {formatValue(
                                result.modelled.residual_season_nutrient_kg_ha?.[row.key]
                              )}{" "}
                              kg/ha
                            </td>
                            <td className="px-3 py-3 font-mono font-bold text-emerald-800">
                              {formatValue(
                                result.modelled.stage_target_nutrient_g_plot?.[row.key]
                              )}{" "}
                              g/plot
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {result.modelled.liquid_comparison && (
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                      <div className="rounded-xl bg-slate-50 p-4">
                        <p className="text-[11px] font-semibold text-slate-500">
                          Liquid comparison volume
                        </p>
                        <p className="mt-1 text-lg font-black text-slate-800">
                          {formatValue(
                            result.modelled.liquid_comparison.comparison_volume_ml,
                            " ml"
                          )}
                        </p>
                      </div>
                      <div className="rounded-xl bg-slate-50 p-4">
                        <p className="text-[11px] font-semibold text-slate-500">
                          Per-plant comparison
                        </p>
                        <p className="mt-1 text-lg font-black text-slate-800">
                          {formatValue(
                            result.modelled.liquid_comparison.per_plant_comparison_ml,
                            " ml"
                          )}
                        </p>
                      </div>
                      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
                        <p className="text-[11px] font-semibold text-amber-800">
                          Physical pump
                        </p>
                        <p className="mt-1 text-sm font-black text-amber-900">
                          Disabled — comparison only
                        </p>
                      </div>
                    </div>
                  )}
                  {!!result.modelled.liquid_comparison?.constraints.length && (
                    <ul className="list-inside list-disc space-y-1 text-xs text-amber-800">
                      {result.modelled.liquid_comparison.constraints.map((caution) => (
                        <li key={caution}>{caution}</li>
                      ))}
                    </ul>
                  )}
                </>
              ) : (
                <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-4 text-xs leading-relaxed text-amber-900">
                  <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>
                    {result.status === "SOIL_CALIBRATION_REQUIRED"
                      ? "Enter all three validated soil transfer coefficients to calculate an experimental comparison. Without them, sensor mg/kg readings cannot be converted to crop-available kg/ha."
                      : "The reference mode reports the DOA solid-fertilizer schedule only; it does not infer a soil-based deficiency."}
                  </span>
                </div>
              )}

              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <h4 className="mb-2 flex items-center gap-2 text-xs font-bold text-slate-700">
                  <CheckCircle2 className="h-4 w-4 text-emerald-700" />
                  Reference stage: Week {result.plot.stage_week}
                </h4>
                <div className="grid grid-cols-3 gap-3 text-xs">
                  {nutrientRows.map((row) => (
                    <div key={row.key}>
                      <p className="text-slate-500">{row.key}</p>
                      <p className="mt-1 font-mono font-bold text-slate-800">
                        {formatValue(result.reference.stage_nutrient_g_plot[row.key])} g/plot
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {!result && !loading && !error && (
            <p className="rounded-xl bg-slate-50 p-4 text-xs text-slate-500">
              Submit the model inputs to calculate the soil comparison.
            </p>
          )}
        </section>
      </div>

    </div>
  );
}
