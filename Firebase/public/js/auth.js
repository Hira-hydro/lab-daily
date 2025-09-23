import { auth } from "./firebase.js";
import { signInWithEmailAndPassword, onAuthStateChanged, signOut } 
  from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";

// ログイン処理
export function setupLogin() {
  const form = document.getElementById("loginForm");
  const msg = document.getElementById("message");

  if (!form) return; // ログインページだけ

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      await signInWithEmailAndPassword(auth, email, password);
      // ここで遷移
      window.location.href = "dashboard.html";
    } catch (error) {
      msg.textContent = "ログイン失敗: " + error.message;
    }
  });
}

// ダッシュボード用
export function setupDashboard() {
  const welcome = document.getElementById("welcome");
  const logoutBtn = document.getElementById("logoutBtn");

  if (!welcome || !logoutBtn) return;

  onAuthStateChanged(auth, (user) => {
    if (user) {
      welcome.textContent = `ようこそ、${user.email} さん`;
    } else {
      // 未ログインならログインページへ
      window.location.href = "index.html";
    }
  });

  logoutBtn.addEventListener("click", async () => {
    await signOut(auth);
    window.location.href = "index.html";
  });
}
