import { ResponsiveLine } from "@nivo/line";
import { useTheme } from "@mui/material";
import { tokens } from "../theme";

const SensorLine = ({ points, color }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const data = [
    {
      id: "value",
      data: points.length ? points : [{ x: "-", y: 0 }],
    },
  ];

  return (
    <ResponsiveLine
      data={data}
      margin={{ top: 16, right: 16, bottom: 48, left: 52 }}
      xScale={{ type: "point" }}
      yScale={{ type: "linear", min: "auto", max: "auto" }}
      axisBottom={{ tickRotation: -35, tickPadding: 6 }}
      axisLeft={{ tickSize: 4, tickPadding: 4 }}
      enableGridX={false}
      pointSize={6}
      useMesh
      colors={[color || colors.greenAccent[500]]}
      theme={{
        axis: {
          ticks: { text: { fill: colors.grey[100] } },
        },
        tooltip: { container: { color: colors.primary[500] } },
      }}
    />
  );
};

export default SensorLine;
