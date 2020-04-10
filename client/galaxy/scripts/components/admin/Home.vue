<template>
    <div>
<!--        <h2>Administration</h2>-->
        <h2>管理</h2>
<!--        Please visit-->

<!--        <a href="https://galaxyproject.org/admin" target="_blank">the Galaxy administration hub</a> to learn how to keep-->
<!--        your Galaxy in best shape.-->
        <br>
<!--        <h4>Server</h4>-->
        <h4>服务器</h4>
        <ul>
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminDataTypesUrl">Data types</a>-->
                    <a @click.prevent="useRouter" :href="adminDataTypesUrl">数据类型</a>
                </strong>
<!--                - See all datatypes available in this Galaxy.-->
                - 查看此系统中所有可用的数据类型。
            </li>
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminDataTablesUrl">Data tables</a>-->
                    <a @click.prevent="useRouter" :href="adminDataTablesUrl">数据表</a>
                </strong>
<!--                - See all data tables available in this Galaxy.-->
                - 查看此系统中所有可用的数据表。
            </li>
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminDisplayApplicationsUrl">Display applications</a>-->
                    <a @click.prevent="useRouter" :href="adminDisplayApplicationsUrl">显示应用程序</a>
                </strong>
<!--                - See all display applications configured in this Galaxy.-->
                - 查看在这个系统中配置的所有显示应用程序。
            </li>
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminJobsUrl">Manage jobs</a>-->
                    <a @click.prevent="useRouter" :href="adminJobsUrl">管理工作</a>
                </strong>
<!--                - Display all jobs that are currently not finished (i.e., their state is new, waiting, queued, or-->
<!--                running). Administrators are able to cleanly stop long-running jobs.-->
                - 显示当前未完成的所有工作（即，它们的状态为“新建”、“等待”、“排队”或“正在运行”）。管理员能够完全停止长时间运行的工作。
            </li>
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminDMUrl">Local data</a>-->
                    <a @click.prevent="useRouter" :href="adminDMUrl">本地数据</a>
                </strong>
<!--                - Manage the reference (and other) data that is stored within Tool Data Tables. See-->
<!--                <a href="https://galaxyproject.org/admin/tools/data-managers" target="_blank">wiki</a> for details.-->
                - 管理存储在工具数据表中的引用（和其他）数据。
            </li>
        </ul>

<!--        <h4>User Management</h4>-->
        <h4>用户管理</h4>
        <ul>
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminUsersUrl">Users</a>-->
                    <a @click.prevent="useRouter" :href="adminUsersUrl">用户</a>
                </strong>
<!--                - The primary user management interface, displaying information associated with each user and providing-->
<!--                operations for resetting passwords, updating user information, impersonating a user, and more.-->
                - 主用户管理界面，显示与每个用户相关联的信息，并提供重置密码、更新用户信息、模拟用户等操作。
            </li>
            <!-- %if trans.app.config.enable_quotas: -->
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminQuotasUrl">Quotas</a>-->
                    <a @click.prevent="useRouter" :href="adminQuotasUrl">配额</a>
                </strong>
<!--                - Manage user space quotas. See-->
<!--                <a href="https://galaxyproject.org/admin/disk-quotas" target="_blank">wiki</a> for details.-->
                - 管理用户空间配额。详情见<a href="https://galaxyproject.org/admin/disk-quotas" target="_blank">wiki</a>。
            </li>
            <!-- %endif -->
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminGroupsUrl">Groups</a>-->
                    <a @click.prevent="useRouter" :href="adminGroupsUrl">组别</a>
                </strong>
<!--                - A view of all groups along with the members of the group and the roles associated with each group.-->
                - 所有组以及组成员和与每个组关联的角色视图。
            </li>
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminRolesUrl">Roles</a>-->
                    <a @click.prevent="useRouter" :href="adminRolesUrl">角色</a>
                </strong>
<!--                - A view of all non-private roles along with the role type, and the users and groups that are-->
<!--                associated, with the role. Also includes a view of the data library datasets that are associated with-->
<!--                the role and the permissions applied to each dataset.-->
                - 所有非私有角色以及角色类型、与角色关联的用户和组的视图。还包括与应用于每个数据集的角色和权限相关联的数据库、数据集的视图。
            </li>
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminFormsUrl">Forms</a>-->
                    <a @click.prevent="useRouter" :href="adminFormsUrl">表单</a>
                </strong>
<!--                - Manage local form definitions.-->
                - 管理本地表单定义。
            </li>
        </ul>

<!--        <h4>Tool Management</h4>-->
        <h4>工具管理</h4>
        <ul>
            <li v-if="isToolShedInstalled">
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminToolshedUrl">Install new tools</a>-->
                    <a @click.prevent="useRouter" :href="adminToolshedUrl">安装新的工具</a>
                </strong>
                - Search and install new tools and other Galaxy utilities from the Tool Shed. See
                <a href="https://galaxyproject.org/admin/tools/add-tool-from-toolshed-tutorial" target="_blank"
                    >the tutorial</a>.
                - 从工具库中搜索并安装新工具和其他Galaxy实用程序。
                <a href="https://galaxyproject.org/admin/tools/add-tool-from-toolshed-tutorial" target="_blank">查看教程</a>。
            </li>
            <li v-if="installingRepositoryIds">
<!--                <strong>Monitor installation</strong> - View the status of tools that are being currently installed.-->
                <strong>监控安装</strong> - 查看当前安装的工具状态。
            </li>
            <template v-if="isRepoInstalled">
                <li>
<!--                    <strong>Manage tools</strong> - View and administer installed tools and utilities on this Galaxy.-->
                    <strong>管理工具</strong> - 查看和管理此系统上已安装的工具和实用程序。
                </li>
<!--                <li><strong>Manage metadata</strong> - Select on which repositories you want to reset metadata.</li>-->
                <li><strong>管理元数据</strong> - 选择要重置元数据的存储库。</li>
            </template>
            <li>
                <strong>
<!--                    <a @click.prevent="useRouter" :href="adminToolVersionsUrl">View lineage</a>-->
                    <a @click.prevent="useRouter" :href="adminToolVersionsUrl">查看家系</a>
                </strong>
<!--                - A view of a version lineages for all installed tools. Useful for debugging.-->
                - 所有已安装工具的版本家系视图。用于调试。
            </li>
            <li>
                <strong>
<!--                    <a :href="migrationStagesUrl">View migration stages</a>-->
                    <a :href="migrationStagesUrl">查看迁移阶段</a>
                </strong>
<!--                - See the list of migration stages that moved sets of tools from the distribution to the Tool Shed.-->
                - 请参阅将工具集从分发版移动到工具库的迁移阶段列表。
            </li>
        </ul>
    </div>
</template>

<script>
import { getAppRoot } from "onload/loadConfig";
import { getGalaxyInstance } from "app";

const root = getAppRoot();

export default {
    props: {
        installingRepositoryIds: {
            type: String,
            required: true
        },
        isRepoInstalled: {
            type: Boolean,
            required: true
        },
        isToolShedInstalled: {
            type: Boolean,
            required: true
        }
    },
    methods: {
        useRouter: function(ev) {
            const Galaxy = getGalaxyInstance();
            Galaxy.page.router.push(ev.target.pathname.slice(root.length));
        }
    },
    computed: {
        migrationStagesUrl: () => `${root}admin/review_tool_migration_stages`, // NOT ROUTER
        adminDataTypesUrl: () => `${root}admin/data_types`,
        adminDataTablesUrl: () => `${root}admin/data_tables`,
        adminDisplayApplicationsUrl: () => `${root}admin/display_applications`,
        adminJobsUrl: () => `${root}admin/jobs`,
        adminDMUrl: () => `${root}admin/data_manager`,
        adminUsersUrl: () => `${root}admin/users`,
        adminQuotasUrl: () => `${root}admin/quotas`,
        adminGroupsUrl: () => `${root}admin/groups`,
        adminRolesUrl: () => `${root}admin/roles`,
        adminFormsUrl: () => `${root}admin/forms`,
        adminToolshedUrl: () => `${root}admin/toolshed`,
        adminToolVersionsUrl: () => `${root}admin/tool_versions`
    }
};
</script>
