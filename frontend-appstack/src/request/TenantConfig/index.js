import { get, put } from "@/request";

export const getTenantConfig = async (tenant, app_id) => {
  try {
    let url = `/${tenant}/${app_id}/oid/tenant-config`;
    const response = await get(url);
    return response.data;
  } catch (error) {
    console.error("Error get tenant configuration:", error);
    throw error;
  }
}


export const updateContractInfo = async (tenant, app_id, data) => {
  try {
    let url = `/${tenant}/${app_id}/oid/tenant-config/update-contract-info`;
    const response = await put(url, data);
    return response.data;
  } catch (error) {
    console.error("Error updating contract info:", error);
    throw error;
  }
}