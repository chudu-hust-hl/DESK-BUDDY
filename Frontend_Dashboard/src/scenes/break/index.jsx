import { useEffect, useState } from "react";
import { Box, Button, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import Header from "../../components/Header";
import { sendCommand } from "../../api";

const FOCUS_SECONDS = 25 * 60;
const BREAK_SECONDS = 5 * 60;

function label(total) {
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

const BreakReminder = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [mode, setMode] = useState("focus");
  const [remaining, setRemaining] = useState(FOCUS_SECONDS);
  const [running, setRunning] = useState(false);
  const [note, setNote] = useState("");

  useEffect(() => {
    if (!running) {
      return undefined;
    }
    const id = setInterval(() => {
      setRemaining((value) => value - 1);
    }, 1000);
    return () => clearInterval(id);
  }, [running]);

  useEffect(() => {
    if (remaining > 0) {
      return;
    }
    if (mode === "focus") {
      setMode("break");
      setRemaining(BREAK_SECONDS);
      setRunning(true);
      sendCommand({ break: true })
        .then(() => setNote("Đã gửi lệnh kêu buzzer trên node."))
        .catch((err) => setNote(`Hết phiên tập trung. ${err.message}`));
    } else {
      setRunning(false);
      setMode("focus");
      setRemaining(FOCUS_SECONDS);
      setNote("Hết giờ nghỉ. Bắt đầu phiên tập trung mới khi sẵn sàng.");
    }
  }, [remaining, mode]);

  const reset = () => {
    setRunning(false);
    setMode("focus");
    setRemaining(FOCUS_SECONDS);
    setNote("");
  };

  return (
    <Box m="20px">
      <Header
        title="NHẮC NGHỈ"
        subtitle="25 phút tập trung, 5 phút nghỉ. Khi sang giờ nghỉ, web gửi lệnh break tới node."
      />
      <Box backgroundColor={colors.primary[400]} p="24px" maxWidth="480px">
        <Typography variant="h3" color={colors.greenAccent[400]}>
          {mode === "focus" ? "Đang tập trung" : "Đang nghỉ"}
        </Typography>
        <Typography variant="h1" color={colors.grey[100]} my="16px">
          {label(Math.max(remaining, 0))}
        </Typography>
        <Box display="flex" gap="12px">
          <Button variant="contained" color="secondary" onClick={() => setRunning((value) => !value)}>
            {running ? "Tạm dừng" : "Bắt đầu"}
          </Button>
          <Button variant="outlined" color="secondary" onClick={reset}>
            Đặt lại
          </Button>
          <Button
            variant="outlined"
            color="secondary"
            onClick={() =>
              sendCommand({ break: true })
                .then(() => setNote("Đã gửi thử lệnh nghỉ."))
                .catch((err) => setNote(err.message))
            }
          >
            Thử còi
          </Button>
        </Box>
        {note ? (
          <Typography color={colors.grey[100]} mt="16px">
            {note}
          </Typography>
        ) : null}
      </Box>
    </Box>
  );
};

export default BreakReminder;
