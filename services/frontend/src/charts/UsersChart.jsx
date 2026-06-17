import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement
} from "chart.js";

import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement);

export default function UsersChart() {

  const data = {
    labels: ["18-25", "25-35", "35-50"],
    datasets: [
      {
        label: "Users",
        data: [120, 400, 200]
      }
    ]
  };

  return <Bar data={data} />;
}