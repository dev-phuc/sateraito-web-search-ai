import { get } from "@/request";

export const fetchOperationLogs = async (tenant, app_id, params) => {
  try {
    let url = `/${tenant}/${app_id}/oid/operation-log`;
    params = params || {};
    console.log(params);
    
    const response = await get(url, params);
    return response.data;
  } catch (error) {
    console.error("Error fetching operation logs:", error);
    throw error;
  }
}
