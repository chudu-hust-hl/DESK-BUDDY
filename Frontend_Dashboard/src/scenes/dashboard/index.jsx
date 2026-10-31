import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import Header from "../../components/Header";
import StatBox from "../../components/StatBox";
import SensorLine from "../../components/SensorLine";
import ThermostatIcon from "@mui/icons-material/Thermostat";
import WbSunnyIcon from "@mui/icons-material/WbSunny";
import LightIcon from "@mui/icons-material/Light";
import { Air } from "@mui/icons-material";
import { getHistory, getLatest } from "../../api";
import { usePoll } from "../../hooks/usePoll";

function clock(ts) {
  return new Date(ts * 1000).toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function points(rows, field) {
  return (rows || []).slice(-20).map((row) => ({
    x: clock(row.ts),
    y: Number(row[field]),
  }));
}

const charts = [
  { title: "Nhiệt độ (°C)", field: "tempC", color: "#4cceac" },
  { title: "Độ ẩm (%)", field: "humidity", color: "#6870fa" },
  { title: "Ánh sáng (ADC)", field: "lightRaw", color: "#ffc107" },
  { title: "Không khí (ADC)", field: "airRaw", color: "#f44336" },
];

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const latest = usePoll(getLatest, 3000);
  const history = usePoll(getHistory, 3000);
  const reading = latest.data && latest.data.data;
  const rows = history.data && history.data.data ? history.data.data : [];
  const active = latest.data && latest.data.alerts ? latest.data.alerts : [];

  const value = (field, suffix) => (reading ? `${reading[field]}${suffix}` : "—");

  return (
    <Box m="20px">
      <Header
        title="DESK BUDDY"
        subtitle="Nhiệt độ, độ ẩm, ánh sáng và không khí tại bàn. Số liệu làm mới mỗi 3 giây."
      />
      {latest.error || history.error ? (
        <Typography color={colors.redAccent[400]} mb="16px">
          Chưa gọi được API. Chạy backend ở cổng 5000. {latest.error || history.error}
        </Typography>
      ) : null}
      {active.length > 0 ? (
        <Typography color={colors.redAccent[400]} mb="16px">
          {active.map((item) => item.message).join(" ")}
        </Typography>
      ) : null}

      <Box display="grid" gridTemplateColumns="repeat(12, 1fr)" gridAutoRows="140px" gap="20px">
        <StatCard span={3} colors={colors} title={value("tempC", "°C")} subtitle="Nhiệt độ" icon={<ThermostatIcon sx={{ fontSize: "32px" }} />} />
        <StatCard span={3} colors={colors} title={value("humidity", "%")} subtitle="Độ ẩm" icon={<WbSunnyIcon sx={{ fontSize: "32px" }} />} />
        <StatCard span={3} colors={colors} title={value("lightRaw", "")} subtitle="Ánh sáng ADC" icon={<LightIcon sx={{ fontSize: "32px" }} />} />
        <StatCard span={3} colors={colors} title={value("airRaw", "")} subtitle="Không khí ADC" icon={<Air sx={{ fontSize: "32px" }} />} />

        {charts.map((chart) => (
          <Box
            key={chart.field}
            gridColumn="span 6"
            gridRow="span 2"
            backgroundColor={colors.primary[400]}
          >
            <Typography variant="h4" fontWeight="bold" color={colors.greenAccent[500]} p="16px 24px 0">
              {chart.title}
            </Typography>
            <Box height="220px">
              {rows.length === 0 ? (
                <Typography color={colors.grey[100]} p="24px">
                  Chưa có lịch sử.
                </Typography>
              ) : (
                <SensorLine points={points(rows, chart.field)} color={chart.color} />
              )}
            </Box>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

const StatCard = ({ span, colors, title, subtitle, icon }) => (
  <Box
    gridColumn={`span ${span}`}
    backgroundColor={colors.primary[400]}
    display="flex"
    alignItems="center"
    justifyContent="center"
  >
    <StatBox
      title={title}
      subtitle={subtitle}
      icon={<Box sx={{ color: colors.greenAccent[600] }}>{icon}</Box>}
    />
  </Box>
);

export default Dashboard;
