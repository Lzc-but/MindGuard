<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { createUser, deleteUser, listUsers, updateUser, type UserItem } from "../../api/admin";

const users = ref<UserItem[]>([]);
const tableLoading = ref(false);
const dialogVisible = ref(false);
const dialogTitle = ref("新增用户");
const dialogLoading = ref(false);

const dialogForm = reactive({
  id: "",
  username: "",
  password: "",
  role: "user" as "admin" | "user",
  display_name: "",
  status: "active" as "active" | "disabled",
});
const isEdit = ref(false);

const statusTagType = (status: string) => (status === "active" ? "success" : "danger");
const statusLabel = (status: string) => (status === "active" ? "正常" : "已禁用");

const formatDateTime = (_row: unknown, _column: unknown, cellValue: string) => {
  if (!cellValue) return "-";
  return new Date(cellValue).toLocaleString("zh-CN");
};

// ---- 数据加载 ----
const fetchUsers = async () => {
  tableLoading.value = true;
  try {
    users.value = await listUsers();
  } finally {
    tableLoading.value = false;
  }
};

// ---- 新增 ----
const openCreate = () => {
  isEdit.value = false;
  dialogTitle.value = "新增用户";
  dialogForm.id = "";
  dialogForm.username = "";
  dialogForm.password = "";
  dialogForm.role = "user";
  dialogForm.display_name = "";
  dialogForm.status = "active";
  dialogVisible.value = true;
};

// ---- 编辑 ----
const openEdit = (user: UserItem) => {
  isEdit.value = true;
  dialogTitle.value = `编辑用户：${user.username}`;
  dialogForm.id = user.id;
  dialogForm.username = user.username;
  dialogForm.password = "";
  dialogForm.role = user.role as "admin" | "user";
  dialogForm.display_name = user.display_name;
  dialogForm.status = user.status as "active" | "disabled";
  dialogVisible.value = true;
};

// ---- 提交 ----
const submit = async () => {
  dialogLoading.value = true;
  try {
    if (isEdit.value) {
      const payload: Record<string, string> = {
        role: dialogForm.role,
        display_name: dialogForm.display_name,
        status: dialogForm.status,
      };
      if (dialogForm.password) {
        payload.password = dialogForm.password;
      }
      await updateUser(dialogForm.id, payload);
      ElMessage.success("更新成功");
    } else {
      await createUser({
        username: dialogForm.username,
        password: dialogForm.password,
        role: dialogForm.role,
        display_name: dialogForm.display_name,
      });
      ElMessage.success("新增成功");
    }
    dialogVisible.value = false;
    await fetchUsers();
  } finally {
    dialogLoading.value = false;
  }
};

// ---- 删除 ----
const doDelete = async (user: UserItem) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户「${user.username}」吗？`, "删除确认", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
  } catch {
    return;
  }
  try {
    await deleteUser(user.id);
    ElMessage.success("已删除");
    await fetchUsers();
  } catch {
    ElMessage.error("删除失败");
  }
};

onMounted(fetchUsers);
</script>

<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-[#1d1d1f]">用户与权限管理</h2>
      <el-button type="primary" @click="openCreate">+ 新增用户</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="users" v-loading="tableLoading" stripe style="width: 100%">
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="display_name" label="显示名" min-width="100" />
        <el-table-column prop="role" label="角色" width="90">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'warning' : 'info'" size="small">
              {{ row.role === "admin" ? "管理员" : "普通用户" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="170" :formatter="formatDateTime" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" text type="danger" @click="doDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="460px" :close-on-click-modal="false">
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名" v-if="!isEdit">
          <el-input v-model="dialogForm.username" placeholder="英文+数字" maxlength="50" />
        </el-form-item>
        <el-form-item :label="isEdit ? '新密码（留空不变）' : '密码'">
          <el-input
            v-model="dialogForm.password"
            type="password"
            show-password
            placeholder="至少 4 位"
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="显示名">
          <el-input v-model="dialogForm.display_name" placeholder="可选" maxlength="50" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="dialogForm.role" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-radio-group v-model="dialogForm.status">
            <el-radio value="active">正常</el-radio>
            <el-radio value="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>