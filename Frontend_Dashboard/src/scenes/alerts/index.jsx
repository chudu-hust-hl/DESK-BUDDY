import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import Header from "../../components/Header";
import { getAlerts } from "../../api";
import { usePoll } from "../../hooks/usePoll";

function clock(ts) {
  return new Date(ts * 1000).toLocaleString("vi-VN");
}

const Alerts = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const { data, error } = usePoll(getAlerts, 3000);
  const active = data ? data.active : [];
  const recent = data ? data.recent : [];
  const thresholds = data ? data.thresholds : null;

  return (
    <Box m="20px">
      <Header
        title="CẢNH BÁO"
        subtitle="Ngưỡng nóng, ẩm, khí và thiếu sáng. MQ135 là ADC tương đối, không phải ppm."
      />
      {error ? <Typography color={colors.redAccent[400]}>{error}</Typography> : null}
      {thresholds ? (
        <Typography color={colors.grey[100]} mb="16px">
          Ngưỡng: nhiệt độ ≥ {thresholds.tempHighC}°C, ẩm ≥ {thresholds.humidityHigh}%, khí ≥ {thresholds.airHighRaw}, sáng ≤ {thresholds.lightLowRaw}.
        </Typography>
      ) : null}
      <Typography variant="h4" color={colors.greenAccent[400]} mb="8px">
        Đang xảy ra
      </Typography>
      {active.length === 0 ? (
        <Typography color={colors.grey[100]} mb="20px">
          Không có cảnh báo trên mẫu mới nhất.
        </Typography>
      ) : (
        active.map((item) => (
          <Typography key={item.code} color={colors.redAccent[400]} mb="8px">
            {item.message} ({item.value})
          </Typography>
        ))
      )}
      <Typography variant="h4" color={colors.greenAccent[400]} mt="20px" mb="8px">
        Gần đây
      </Typography>
      {recent.length === 0 ? (
        <Typography color={colors.grey[100]}>Chưa có lần vượt ngưỡng nào trong lịch sử gần.</Typography>
      ) : (
        recent.map((item, index) => (
          <Typography key={`${item.ts}-${item.code}-${index}`} color={colors.grey[100]} mb="6px">
            {clock(item.ts)} · {item.message}
          </Typography>
        ))
      )}
    </Box>
  );
};

export default Alerts;
