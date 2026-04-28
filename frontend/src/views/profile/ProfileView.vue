<script setup lang="ts">
import { computed } from "vue";
import { useAuthStore } from "../../stores/auth";

const authStore = useAuthStore();

const roleText = computed(() => {
  if (authStore.user?.role === "admin") return "管理员";
  if (authStore.user?.role === "user") return "普通用户";
  return "-";
});
</script>

<template>
  <h2 class="page-title">个人信息</h2>
  <el-card>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="用户名">{{ authStore.user?.username || "-" }}</el-descriptions-item>
      <el-descriptions-item label="角色">{{ roleText }}</el-descriptions-item>
      <el-descriptions-item label="登录状态">
        {{ authStore.isLoggedIn ? "已登录" : "未登录" }}
      </el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>
