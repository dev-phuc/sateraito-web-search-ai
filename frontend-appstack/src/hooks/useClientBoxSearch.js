import { useContext } from "react";

import BoxSearchContext from "@/contexts/BoxSearchContext";

const useBoxSearch = () => {
  const context = useContext(BoxSearchContext);
  
  if (!context)
    throw new Error("BoxSearchContext must be placed within BoxSearchProvider");
  
  return context;
};

export default useBoxSearch;
