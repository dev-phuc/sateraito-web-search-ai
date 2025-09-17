import { get, put } from "@/request";

export const getUserConfigRequest = async (tenant, app_id) => {
  try {
    let url = `/${tenant}/${app_id}/oid/user-config`;
    const response = await get(url);
    return response.data;
  } catch (error) {
    console.error('Failed to get user settings:', error);
    throw error;
  }
}

export const updateUserConfigRequest = async (tenant, app_id, data) => {
  try {
    let url = `/${tenant}/${app_id}/oid/user-config`;
    const response = await put(url, data);
    return response.data;
  } catch (error) {
    console.error('Failed to update user settings:', error);
    throw error;
  }
}
