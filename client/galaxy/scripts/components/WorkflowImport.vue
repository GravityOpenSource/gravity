<template>
    <b-form @submit="submit">
<!--        <b-card title="Import Workflow">-->
        <b-card title="导入流程">
            <b-alert :show="hasErrorMessage" variant="danger">{{ errorMessage }}</b-alert>
<!--            <p>Please provide a Galaxy workflow export URL or a workflow file.</p>-->
            <p>请提供流程导出URL或流程文件。</p>
<!--            <b-form-group label="Archived Workflow URL">-->
            <b-form-group label="存档流程的URL">
                <b-form-input id="workflow-import-url-input" type="url" v-model="sourceURL" />
<!--                If the workflow is accessible via a URL, enter the URL above and click Import.-->
                如果可以通过URL访问流程，请在上方输入URL，然后单击“导入”。
            </b-form-group>
<!--            <b-form-group label="Archived Workflow File">-->
            <b-form-group label="存档流程的文件">
                <b-form-file v-model="sourceFile" placeholder="没有选择文件" browse-text="浏览" />
<!--                If the workflow is in a file on your computer, choose it and then click Import.-->
                如果流程在计算机上的文件中，请选择它，然后单击“导入”。
            </b-form-group>
<!--            <b-button id="workflow-import-button" type="submit">Import workflow</b-button>-->
            <b-button id="workflow-import-button" type="submit">导入流程</b-button>
            <div class="mt-4">
<!--                <h4>Import a Workflow from myExperiment</h4>-->
                <h4>从myExperiment导入工作流程</h4>
<!--                <a :href="myexperiment_target_url">Visit myExperiment</a>-->
                <a :href="myexperiment_target_url">访问 myExperiment</a>
<!--                <div class="form-text">Click the link above to visit myExperiment and search for Galaxy workflows.</div>-->
                <div class="form-text">单击上面的链接访问myExperiment并搜索流程。</div>
            </div>
        </b-card>
    </b-form>
</template>
<script>
import { getAppRoot } from "onload/loadConfig";
import { getGalaxyInstance } from "app";
import axios from "axios";
import Vue from "vue";
import BootstrapVue from "bootstrap-vue";

Vue.use(BootstrapVue);

export default {
    data() {
        const Galaxy = getGalaxyInstance();
        return {
            sourceFile: null,
            sourceURL: null,
            errorMessage: null,
            myexperiment_target_url: `http://${Galaxy.config.myexperiment_target_url}/galaxy?galaxy_url=${
                window.location.protocol
            }//${window.location.host}`
        };
    },
    computed: {
        hasErrorMessage() {
            return this.errorMessage != null;
        }
    },
    methods: {
        submit: function(ev) {
            ev.preventDefault();
            if (!this.sourceFile && !this.sourceURL) {
                // this.errorMessage = "You must provide a workflow archive URL or file.";
                this.errorMessage = "您必须提供工流程存档URL或文件。";
            } else {
                const formData = new FormData();
                formData.append("archive_file", this.sourceFile);
                formData.append("archive_source", this.sourceURL);
                axios
                    .post(`${getAppRoot()}api/workflows`, formData)
                    .then(response => {
                        window.location = `${getAppRoot()}workflows/list?message=${
                            response.data.message
                        }&status=success`;
                    })
                    .catch(error => {
                        const message = error.response.data && error.response.data.err_msg;
                        // this.errorMessage = message || "Import failed for an unknown reason.";
                        this.errorMessage = message || "导入失败，原因未知。";
                    });
            }
        }
    }
};
</script>
