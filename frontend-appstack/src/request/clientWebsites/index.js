import { get, post, put, deleteReq } from "@/request";
import { generateTokenByTenant } from "@/utils";

export const fetchClientWebsitesList = async (tenant, app_id) => {
  try {
    let url = `/${tenant}/${app_id}/oid/client_websites`;
    const response = await get(url);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch client websites list:', error);
    throw error;
  }
}

export const createClientWebsites = async (tenant, app_id, data) => {
  try {
    let url = `/${tenant}/${app_id}/oid/client_websites`;
    const response = await post(url, data);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch client websites list:', error);
    throw error;
  }
}

export const editClientWebsites = async (tenant, app_id, id, data) => {
  try {
    let url = `/${tenant}/${app_id}/oid/client_websites/${id}`;
    const response = await put(url, data);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch client websites list:', error);
    throw error;
  }
}

export const deleteClientWebsites = async (tenant, app_id, id) => {
  try {
    let url = `/${tenant}/${app_id}/oid/client_websites/${id}`;
    const response = await deleteReq(url);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch client websites list:', error);
    throw error;
  }
}

export const getFirebaseTokenForClient = async (tenant, app_id, clientWebsite) => {
  try {
    let url = `/${tenant}/${app_id}/client/client_websites/firebase_token`;

    const token = generateTokenByTenant(tenant, clientWebsite);
    const params = {
    };
    const headers = {
      'Authorization': `Bearer ${token}`,
    };

    const response = await get(url, params, headers);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch client websites list:', error);
    throw error;
  }
}