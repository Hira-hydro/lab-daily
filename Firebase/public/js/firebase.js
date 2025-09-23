// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-analytics.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyC2bTa1JSmKTKhIubtu6ZhF8GHHXVENOXk",
  authDomain: "lab-dairy.firebaseapp.com",
  projectId: "lab-dairy",
  storageBucket: "lab-dairy.firebasestorage.app",
  messagingSenderId: "409314753820",
  appId: "1:409314753820:web:890476599a182920f2ced9",
  measurementId: "G-DVSL9ETRH7",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
