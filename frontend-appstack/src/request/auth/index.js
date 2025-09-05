import { get, post } from "@/request";
import { SERVER_URL } from "@/constants";

export const getMe = async (tenant='vn2.sateraito.co.jp', app_id='default') => {
  try {
    let url = `/${tenant}/${app_id}/user/oid/getme`;
    const response = await get(url);
    return response.data;
  } catch (error) {
    console.error('Token verification failed:', error);
    throw error;
  }
}

export const getAccessToken = async () => {
  try {
    const response = await get('/auth/oid/access-token');
    return response.data;
  } catch (error) {
    console.error('Failed to get access token:', error);
    throw error;
  }
}

export const logout = async (tenant, app_id) => {
  try {
    const url = `/${tenant}/${app_id}/user/oid/logout`;
    const response = await post(url);
    return response.data;
  } catch (error) {
    console.error('Logout failed:', error);
    throw error;
  }
}

export const openPopupLoginWithGoogle = async (tenant, app_id) => {
  const loginUrl = `${SERVER_URL}/${tenant}/${app_id}/user/login`;

  // Popup center display
  const width = 600;
  const height = 700;
  const left = ((window.innerWidth + 80) - width) / 2;
  const top = ((window.innerHeight + 200) - height) / 2;

  const popup = window.open(
    loginUrl,
    'Google Login',
    `width=${width},height=${height},top=${top},left=${left},resizable=yes,scrollbars=yes,status=yes`
  );
  
  if (!popup) {
    throw new Error('Popup blocked or failed to open');
  }

  // Trigger event listener for message from popup or popup closed
  return new Promise((resolve, reject) => {
    const interval = setInterval(() => {
      if (popup.closed) {
        clearInterval(interval);
        window.removeEventListener('message', messageHandler);
        reject(new Error('Popup closed by user'));
      }
    }, 500);

    const messageHandler = (event) => {
      if (event.origin !== SERVER_URL) {
        return;
      }
      const { data } = event;
      if (data === 'login_success') {
        clearInterval(interval);
        window.removeEventListener('message', messageHandler);
        popup.close();
        resolve(data);
      }
    };

    window.addEventListener('message', messageHandler);
  });
}