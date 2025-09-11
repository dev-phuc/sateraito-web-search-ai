import { get, put } from "@/request";
import { generateTokenByTenant } from "@/utils";

export const getLLMConfiguration = async (tenant, app_id) => {
  try {
    let url = `/${tenant}/${app_id}/oid/llm-configuration`;
    const response = await get(url);
    return response.data;
  } catch (error) {
    console.error("Error fetching LLM configuration:", error);
    throw error;
  }
}

export const getLLMConfigurationForClient = async (tenant, app_id, clientWebsite) => {
  try {
    let url = `/${tenant}/${app_id}/client/llm-configuration`;

    const { origin, href } = clientWebsite;
    const token = generateTokenByTenant(tenant);

    const params = {
      cw_o: origin,
      cw_h: href
    };
    const headers = {
      'Authorization': `Bearer ${token}`
    };

    const response = await get(url, params, headers);
    return response.data;
  } catch (error) {
    console.error("Error fetching LLM configuration:", error);
    throw error;
  }
}

export const editLLMConfiguration = async (tenant, app_id, data) => {
  try {
    let url = `/${tenant}/${app_id}/oid/llm-configuration`;
    const response = await put(url, data);
    return response.data;
  } catch (error) {
    console.error("Error editing LLM configuration:", error);
    throw error;
  }
}
