import { postStream } from "@/request";
import { generateTokenByTenant } from "@/utils";


export const searchWebActionLLMClient = async (tenant, app_id, clientWebsite, query, onStream) => {
  try {
    const url = `/${tenant}/${app_id}/client/llm-actions/search-web`;
    const params = {
      query,
      tenant,
      app_id
    };
    const token = generateTokenByTenant(tenant, clientWebsite);
    const headers = {
      'Authorization': `Bearer ${token}`,
    };
    const response = await postStream(url, params, headers, onStream);
    return response.data;
  } catch (error) {
    console.error("Error fetching LLM configuration:", error);
    throw error;
  }
}
