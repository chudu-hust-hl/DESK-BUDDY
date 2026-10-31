import { useEffect, useState } from "react";

export function usePoll(fetcher, ms = 3000) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let stop = false;
    const tick = () => {
      fetcher()
        .then((next) => {
          if (!stop) {
            setData(next);
            setError("");
          }
        })
        .catch((err) => {
          if (!stop) {
            setError(err.message || "Không gọi được API");
          }
        });
    };
    tick();
    const id = setInterval(tick, ms);
    return () => {
      stop = true;
      clearInterval(id);
    };
  }, [fetcher, ms]);

  return { data, error };
}
