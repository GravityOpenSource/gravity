<template>
    <div>
        <span>本机序列号：{{ machineCode }} </span>
        <br/>
        <span style="width: 360px; word-break: break-word; display: inline-block">License：{{ license }} </span>
        <br/>
        <span>有效期：{{ expire }}</span>
        <br/>
    </div>
</template>

<script>
import { getAppRoot } from "onload/loadConfig";
import axios from "axios";

export default {
    data() {
        return {
            machineCode:'',
            license: '',
            expire: '',
        };
    },

    created() {
        axios.get(`${getAppRoot()}admin/license_info`)
            .then(response => {
                this.machineCode = response.data.machine_code;
                this.license = response.data.license;
                this.expire = response.data.expire;
            })
            .catch(error => {
                console.error(error);
            });
    }
};
</script>
