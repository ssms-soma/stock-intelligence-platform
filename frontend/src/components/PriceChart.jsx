import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatCurrencyByTicker } from "../utils/marketUtils";

const PERIOD_OPTIONS = [
  { label: "1D", value: "1d" },
  { label: "5D", value: "5d" },
  { label: "1M", value: "1mo" },
  { label: "6M", value: "6mo" },
];

function parseDate(value) {
  const parsedDate = new Date(value);
  return Number.isNaN(parsedDate.getTime()) ? null : parsedDate;
}

function formatAxisDate(value, activePeriod) {
  const parsedDate = parseDate(value);

  if (!parsedDate) {
    return value;
  }

  if (activePeriod === "1d") {
    const hasTime = /T|\d{1,2}:\d{2}/.test(String(value));

    if (hasTime) {
      return parsedDate.toLocaleTimeString(undefined, {
        hour: "numeric",
        minute: "2-digit",
      });
    }

    return parsedDate.toLocaleDateString(undefined, {
      month: "short",
      day: "2-digit",
    });
  }

  if (activePeriod === "5d") {
    return parsedDate.toLocaleDateString(undefined, {
      weekday: "short",
      day: "2-digit",
    });
  }

  if (activePeriod === "1mo") {
    return parsedDate.toLocaleDateString(undefined, {
      month: "short",
      day: "2-digit",
    });
  }

  return parsedDate.toLocaleDateString(undefined, {
    month: "short",
  });
}

function formatTooltipDate(value) {
  const parsedDate = parseDate(value);

  if (!parsedDate) {
    return value;
  }

  return parsedDate.toLocaleString(undefined, {
    month: "short",
    day: "2-digit",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function getAxisSettings(activePeriod) {
  if (activePeriod === "1d") {
    return { interval: "preserveStartEnd", tickCount: 5, minTickGap: 34 };
  }

  if (activePeriod === "5d") {
    return { interval: "preserveStartEnd", tickCount: 5, minTickGap: 36 };
  }

  if (activePeriod === "1mo") {
    return { interval: 6, tickCount: 5, minTickGap: 42 };
  }

  return { interval: "preserveStartEnd", tickCount: 6, minTickGap: 46 };
}

function formatCloseValue(value) {
  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return value;
  }

  return numberValue.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function PriceChart({ historyData, activePeriod, onPeriodChange, error, ticker }) {
  const axisSettings = getAxisSettings(activePeriod);
  const hasHistory = Array.isArray(historyData) && historyData.length > 0;

  return (
    <div
      style={{
        marginTop: "2rem",
        padding: "1rem",
        border: "1px solid #dbe3ef",
        background: "#ffffff",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "1rem",
          marginBottom: "1rem",
        }}
      >
        <h2 style={{ margin: 0, color: "#0f172a" }}>Price History</h2>

        <div style={{ display: "flex", gap: "0.4rem" }}>
          {PERIOD_OPTIONS.map((period) => {
            const isActive = activePeriod === period.value;

            return (
              <button
                key={period.value}
                onClick={() => onPeriodChange(period.value)}
                style={{
                  padding: "0.45rem 0.65rem",
                  border: `1px solid ${isActive ? "#2563eb" : "#cbd5e1"}`,
                  borderRadius: "999px",
                  background: isActive ? "#2563eb" : "#ffffff",
                  color: isActive ? "#ffffff" : "#334155",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                {period.label}
              </button>
            );
          })}
        </div>
      </div>

      <div style={{ height: "350px" }}>
        {hasHistory ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={historyData} margin={{ right: 12, left: 4, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => formatAxisDate(value, activePeriod)}
                interval={axisSettings.interval}
                tickCount={axisSettings.tickCount}
                minTickGap={axisSettings.minTickGap}
                tick={{ fontSize: 12, fill: "#64748b" }}
                tickLine={false}
              />
              <YAxis domain={["auto", "auto"]} tick={{ fontSize: 12, fill: "#64748b" }} />
              <Tooltip
                labelFormatter={formatTooltipDate}
                formatter={(value) => [
                  ticker
                    ? formatCurrencyByTicker(value, ticker)
                    : formatCloseValue(value),
                  "Close",
                ]}
              />
              <Line
                type="monotone"
                dataKey="close"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div
            style={{
              height: "100%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "1px dashed #cbd5e1",
              color: "#64748b",
              textAlign: "center",
              padding: "1rem",
            }}
          >
            {error || "Price history is temporarily unavailable."}
          </div>
        )}
      </div>
    </div>
  );
}

export default PriceChart;
