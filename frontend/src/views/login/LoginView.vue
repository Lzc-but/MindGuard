<script setup lang="ts">
import { reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const loginRole = ref<"user" | "admin">("user");

const presetCredentials: Record<"user" | "admin", { username: string; password: string }> = {
  user: { username: "user", password: "user123" },
  admin: { username: "admin", password: "admin123" },
};

const form = reactive({
  username: "user",
  password: "user123",
});

// 切换角色时自动填入对应默认账号
watch(loginRole, (role) => {
  form.username = presetCredentials[role].username;
  form.password = presetCredentials[role].password;
});

const submit = async () => {
  loading.value = true;
  try {
    await authStore.doLogin(form);
    ElMessage.success("登录成功");
    const target = authStore.isAdmin ? "/admin" : "/user/chat";
    router.push(target);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div style="min-height: 100vh; display: grid; place-items: center">
    <el-card style="width: 400px">
      <h2 style="margin: 0 0 20px">心护AI 登录</h2>

      <!-- 角色选择 -->
      <div style="display: flex; gap: 8px; margin-bottom: 20px">
        <el-button
          :type="loginRole === 'user' ? 'primary' : ''"
          style="flex: 1"
          @click="loginRole = 'user'"
        >用户登录</el-button>
        <el-button
          :type="loginRole === 'admin' ? 'primary' : ''"
          style="flex: 1"
          @click="loginRole = 'admin'"
        >管理员登录</el-button>
      </div>

      <el-form label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" style="width: 100%" @click="submit">登录</el-button>
      </el-form>
      <p style="font-size: 12px; color: #909399; margin-top: 12px">默认：admin/admin123 或 user/user123</p>
    </el-card>
  </div>
</template>
