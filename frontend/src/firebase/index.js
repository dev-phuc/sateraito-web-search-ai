import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
// import { getAnalytics } from "firebase/analytics";

import { config } from "@/firebase/config";

const firebaseApp = initializeApp(config);
const db = getFirestore(firebaseApp);
// const analytics = getAnalytics(app);

export { db };
export default firebaseApp;
// export { analytics }; 