import { useContext, useEffect } from "react";

import UserConfigContext from "@/contexts/UserConfigContext";

const useUserConfig = () => {
  const context = useContext(UserConfigContext);

  if (!context)
    throw new Error(
      "UserConfigContext must be placed within UserConfigProvider"
    );

  return context;
};

export default useUserConfig;
