<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);

const form = reactive({
  username: "user",
  password: "user123",
});

const submit = async () => {
  loading.value = true;
  try {
    await authStore.doLogin(form);
    ElMessage.success("登录成功");
    router.push("/chat");
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div style="min-height: 100vh; display: grid; place-items: center">
    <el-card style="width: 400px">
      <h2 style="margin: 0 0 20px">心护AI 登录</h2>
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
