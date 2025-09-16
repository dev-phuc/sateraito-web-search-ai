import { get, put } from "@/request";

export const fetchLLMUsage = async (tenant, app_id, params) => {
  try {
    let url = `/${tenant}/${app_id}/oid/llm-usage`;
    const response = await get(url, params);
    return response.data;
  } catch (error) {
    console.error("Error fetching LLM usage:", error);
    throw error;
  }
}

