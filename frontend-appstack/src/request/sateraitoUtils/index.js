import { get, post } from "@/request";

export const getPageInfoByUrl = async (pageUrl) => {
  try {
    let url = `/utils/page-info-by-url`;
    const response = await get(url, { page_url: pageUrl });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch page info:', error);
    throw error;
  }
}