import { Head, Link } from "@inertiajs/react";
import { useState } from "react";
import MainLayout from "../layouts/MainLayout";
import type { User } from "../types";

interface Stats {
  total: number;
  completed?: number;
  pending?: number;
  open?: number;
  closed?: number;
}

interface HistoryPoint {
  date: string;
  total: number;
  open: number;
  closed: number;
}

interface DashboardProps {
  user: User | null;
  taskStats: Stats;
  ticketStats: Stats;
  ticketHistory: {
    weekly: HistoryPoint[];
    monthly: HistoryPoint[];
  };
}

type Period = "weekly" | "monthly";
type LineKey = "total" | "open" | "closed";

const LINE_COLORS: Record<LineKey, string> = {
  total: "#8b5cf6",
  open: "#3b82f6",
  closed: "#6b7280",
};

function TicketChart({
  data,
  period,
  onPeriodChange,
}: {
  data: HistoryPoint[];
  period: Period;
  onPeriodChange: (p: Period) => void;
}) {
  const [hoveredPoint, setHoveredPoint] = useState<{
    index: number;
    x: number;
    y: number;
  } | null>(null);
  const [visibleLines, setVisibleLines] = useState<Record<LineKey, boolean>>({
    total: true,
    open: true,
    closed: true,
  });

  const toggleLine = (key: LineKey) => {
    setVisibleLines((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  if (data.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Ticket Trends</h2>
          <PeriodToggle period={period} onChange={onPeriodChange} />
        </div>
        <div className="h-48 flex items-center justify-center text-gray-400">
          No data yet. Create some tickets to see trends.
        </div>
      </div>
    );
  }

  const visibleKeys = (Object.keys(visibleLines) as LineKey[]).filter(
    (k) => visibleLines[k]
  );
  const maxValue = Math.max(
    ...data.flatMap((d) => visibleKeys.map((k) => d[k])),
    1
  );
  const chartWidth = 600;
  const chartHeight = 200;
  const padding = { top: 20, right: 20, bottom: 40, left: 40 };
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  const xScale = (i: number) =>
    padding.left + (i / (data.length - 1 || 1)) * innerWidth;
  const yScale = (v: number) =>
    padding.top + innerHeight - (v / maxValue) * innerHeight;

  const createPath = (key: LineKey) =>
    data
      .map((d, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(d[key])}`)
      .join(" ");

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Ticket Trends</h2>
        <PeriodToggle period={period} onChange={onPeriodChange} />
      </div>

      <div className="relative">
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="w-full h-48"
          preserveAspectRatio="xMidYMid meet"
          onMouseLeave={() => setHoveredPoint(null)}
        >
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct) => (
            <g key={pct}>
              <line
                x1={padding.left}
                y1={padding.top + pct * innerHeight}
                x2={chartWidth - padding.right}
                y2={padding.top + pct * innerHeight}
                stroke="#e5e7eb"
                strokeDasharray="4"
              />
              <text
                x={padding.left - 8}
                y={padding.top + pct * innerHeight + 4}
                fontSize="10"
                textAnchor="end"
                fill="#9ca3af"
              >
                {Math.round(maxValue * (1 - pct))}
              </text>
            </g>
          ))}

          {/* Lines with transition */}
          {(["total", "open", "closed"] as LineKey[]).map((key) => (
            <path
              key={key}
              d={createPath(key)}
              fill="none"
              stroke={LINE_COLORS[key]}
              strokeWidth={hoveredPoint !== null ? 3 : 2}
              opacity={visibleLines[key] ? 1 : 0}
              className="transition-all duration-300"
            />
          ))}

          {/* Hover zones and data points */}
          {data.map((d, i) => (
            <g key={d.date}>
              {/* Invisible hover zone */}
              <rect
                x={xScale(i) - 20}
                y={padding.top}
                width={40}
                height={innerHeight}
                fill="transparent"
                onMouseEnter={() =>
                  setHoveredPoint({ index: i, x: xScale(i), y: padding.top })
                }
              />

              {/* Data points */}
              {(["total", "open", "closed"] as LineKey[]).map((key) => (
                <circle
                  key={key}
                  cx={xScale(i)}
                  cy={yScale(d[key])}
                  r={hoveredPoint?.index === i ? 6 : 4}
                  fill={LINE_COLORS[key]}
                  opacity={visibleLines[key] ? 1 : 0}
                  className="transition-all duration-150"
                />
              ))}

              {/* X-axis label */}
              <text
                x={xScale(i)}
                y={chartHeight - 10}
                fontSize="9"
                textAnchor="middle"
                fill="#6b7280"
              >
                {formatDate(d.date, period)}
              </text>
            </g>
          ))}

          {/* Hover line */}
          {hoveredPoint !== null && (
            <line
              x1={hoveredPoint.x}
              y1={padding.top}
              x2={hoveredPoint.x}
              y2={padding.top + innerHeight}
              stroke="#9ca3af"
              strokeWidth={1}
              strokeDasharray="4"
            />
          )}
        </svg>

        {/* Tooltip */}
        {hoveredPoint !== null && (
          <div
            className="absolute bg-gray-900 text-white text-xs rounded-lg py-2 px-3 shadow-lg pointer-events-none z-10"
            style={{
              left: `${(hoveredPoint.x / chartWidth) * 100}%`,
              top: "10px",
              transform: "translateX(-50%)",
            }}
          >
            <div className="font-semibold mb-1">
              {formatDate(data[hoveredPoint.index].date, period)}
            </div>
            {visibleLines.total && (
              <div className="flex items-center gap-2">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: LINE_COLORS.total }}
                />
                Total: {data[hoveredPoint.index].total}
              </div>
            )}
            {visibleLines.open && (
              <div className="flex items-center gap-2">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: LINE_COLORS.open }}
                />
                Open: {data[hoveredPoint.index].open}
              </div>
            )}
            {visibleLines.closed && (
              <div className="flex items-center gap-2">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: LINE_COLORS.closed }}
                />
                Closed: {data[hoveredPoint.index].closed}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Clickable Legend */}
      <div className="flex justify-center gap-6 mt-2">
        {(["total", "open", "closed"] as LineKey[]).map((key) => (
          <button
            key={key}
            onClick={() => toggleLine(key)}
            className={`flex items-center gap-1.5 transition-opacity ${visibleLines[key] ? "opacity-100" : "opacity-40"
              }`}
          >
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: LINE_COLORS[key] }}
            />
            <span className="text-xs text-gray-600 capitalize">{key}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function formatDate(date: string, period: Period): string {
  if (period === "monthly") {
    const [year, month] = date.split("-");
    return `${month}/${year.slice(2)}`;
  }
  const parts = date.split("-");
  return `${parts[1]}/${parts[2]}`;
}

function PeriodToggle({
  period,
  onChange,
}: {
  period: Period;
  onChange: (p: Period) => void;
}) {
  return (
    <div className="flex bg-gray-100 rounded-lg p-1">
      <button
        className={`px-3 py-1 text-xs rounded-md transition ${period === "weekly"
            ? "bg-white shadow text-gray-900"
            : "text-gray-500 hover:text-gray-700"
          }`}
        onClick={() => onChange("weekly")}
      >
        Weekly
      </button>
      <button
        className={`px-3 py-1 text-xs rounded-md transition ${period === "monthly"
            ? "bg-white shadow text-gray-900"
            : "text-gray-500 hover:text-gray-700"
          }`}
        onClick={() => onChange("monthly")}
      >
        Monthly
      </button>
    </div>
  );
}

function StatsSection({
  title,
  stats,
  items,
  href,
}: {
  title: string;
  stats: Stats;
  href: string;
  items: { key: keyof Stats; label: string; color: string }[];
}) {
  return (
    <div className="bg-white p-5 rounded-lg shadow-sm border">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">{title}</h2>
        <Link href={href} className="text-sm text-blue-600 hover:text-blue-800">
          View all →
        </Link>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {items.map((item) => (
          <div key={item.key} className="text-center p-2">
            <div
              className={`text-xl font-bold ${item.color.replace("bg-", "text-")}`}
            >
              {(stats[item.key] as number) || 0}
            </div>
            <div className="text-xs text-gray-500">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard({
  user,
  taskStats,
  ticketStats,
  ticketHistory,
}: DashboardProps) {
  const [period, setPeriod] = useState<Period>("weekly");

  const chartData =
    period === "weekly" ? ticketHistory.weekly : ticketHistory.monthly;

  return (
    <MainLayout user={user}>
      <Head title="Dashboard" />
      <div className="p-6 font-sans">
        <h1 className="text-2xl font-bold mb-1">
          Welcome{user ? `, ${user.name}` : ""}!
        </h1>
        <p className="text-gray-500 text-sm mb-6">
          Interactive dashboard •{" "}
          <code className="bg-gray-100 px-1 rounded text-xs">mode="client"</code>
        </p>

        {/* Chart */}
        <div className="mb-6">
          <TicketChart
            data={chartData}
            period={period}
            onPeriodChange={setPeriod}
          />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <StatsSection
            title="My Tasks"
            stats={taskStats}
            href="/tasks"
            items={[
              { key: "total", label: "Total", color: "bg-blue-500" },
              { key: "completed", label: "Done", color: "bg-green-500" },
              { key: "pending", label: "Pending", color: "bg-yellow-500" },
            ]}
          />

          <StatsSection
            title="Tickets"
            stats={ticketStats}
            href="/tickets"
            items={[
              { key: "total", label: "Total", color: "bg-purple-500" },
              { key: "open", label: "Open", color: "bg-blue-500" },
              { key: "closed", label: "Closed", color: "bg-gray-500" },
            ]}
          />
        </div>

        {!user && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
            <strong>Note:</strong> Login to see your personal task statistics.
          </div>
        )}

        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
          <p className="text-blue-800 text-sm">
            <strong>Render Mode:</strong> Client — Hover for tooltips, click legend
            to toggle lines. These interactions require JavaScript.
          </p>
        </div>
      </div>
    </MainLayout>
  );
}
