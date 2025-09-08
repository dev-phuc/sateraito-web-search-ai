import { get, put } from "@/request";

export const getBoxSearchConfig = async (tenant, app_id) => {
  try {
    let url = `/${tenant}/${app_id}/oid/box_search_config`;
    const response = await get(url);
    return response.data;
  } catch (error) {
    console.error('Failed to get box search config:', error);
    throw error;
  }
}

export const editBoxSearchConfig = async (tenant, app_id, data) => {
  try {
    let url = `/${tenant}/${app_id}/oid/box_search_config`;
    const response = await put(url, data);
    return response.data;
  } catch (error) {
    console.error('Failed to edit box search config:', error);
    throw error;
  }
}
