import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export const useJob = (jobId: string) => {
  return useQuery({
    queryKey: ["job", jobId],
    queryFn: () => api.get(`/progress/${jobId}`).then(r => r.data),
    refetchInterval: 2000,
  });
}; 