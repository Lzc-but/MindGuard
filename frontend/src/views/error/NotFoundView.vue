<template>
  <div style="min-height: 100vh; display: grid; place-items: center">
    <el-result icon="warning" title="404" sub-title="页面不存在">
      <template #extra>
        <el-button type="primary" @click="$router.push('/chat')">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>
