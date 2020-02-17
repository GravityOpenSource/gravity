<template>
    <div class="container">
        <div class="row justify-content-md-center">
            <div class="col" :class="{ 'col-lg-6': !isAdmin }">
                <b-alert v-html="registration_warning_message" :show="showRegistrationWarning" variant="info">
                </b-alert>
                <b-alert :show="messageShow" :variant="messageVariant" v-html="messageText" />
                <b-form id="registration" @submit.prevent="submit()">
                    <b-card no-body header="创建账号">
                        <b-card-body>
                            <b-form-group label="邮箱">
                                <b-form-input name="email" type="text" v-model="email" />
                            </b-form-group>
                            <b-form-group label="密码">
                                <b-form-input name="password" type="password" v-model="password" />
                            </b-form-group>
                            <b-form-group label="确认密码">
                                <b-form-input name="confirm" type="password" v-model="confirm" />
                            </b-form-group>
                            <b-form-group label="用户名">
                                <b-form-input name="username" type="text" v-model="username" />
                                <b-form-text
                                    >您的用户名是一个标识符，将用于为您公开共享的信息生成地址。
                                     用户名的长度必须至少为三个字符，并且只包含小写字母、数字、 点、下划线和破折号('.', '_', '-')。
                                     </b-form-text
                                >
                            </b-form-group>
                            <b-form-group
                                v-if="mailing_join_addr && server_mail_configured"
                                label="Subscribe to mailing list"
                            >
                                <input name="subscribe" type="checkbox" v-model="subscribe" />
                            </b-form-group>
                            <b-button name="create" type="submit" :disabled="disableCreate">创建</b-button>
                        </b-card-body>
                        <b-card-footer v-if="!isAdmin">
                            已有账户?
                            <a id="login-toggle" href="javascript:void(0)" role="button" @click.prevent="toggleLogin"
                                >点击这里登录</a
                            >
                        </b-card-footer>
                    </b-card>
                </b-form>
            </div>
            <div v-if="terms_url" class="col">
                <b-embed type="iframe" :src="terms_url" aspect="1by1" />
            </div>
        </div>
    </div>
</template>
<script>
import axios from "axios";
import Vue from "vue";
import BootstrapVue from "bootstrap-vue";
import { getGalaxyInstance } from "app";
import { getAppRoot } from "onload";

Vue.use(BootstrapVue);

export default {
    props: {
        registration_warning_message: {
            type: String,
            required: false
        },
        server_mail_configured: {
            type: Boolean,
            required: false
        },
        mailing_join_addr: {
            type: String,
            required: false
        },
        redirect: {
            type: String,
            required: false
        },
        terms_url: {
            type: String,
            required: false
        }
    },
    data() {
        const galaxy = getGalaxyInstance();
        return {
            disableCreate: false,
            email: null,
            password: null,
            username: null,
            confirm: null,
            subscribe: null,
            messageText: null,
            messageVariant: null,
            session_csrf_token: galaxy.session_csrf_token,
            isAdmin: galaxy.user.isAdmin()
        };
    },
    computed: {
        messageShow() {
            return this.messageText != null;
        },
        showRegistrationWarning() {
            return this.registration_warning_message != null;
        }
    },
    methods: {
        toggleLogin: function() {
            if (this.$root.toggleLogin) {
                this.$root.toggleLogin();
            }
        },
        submit: function(method) {
            this.disableCreate = true;
            const rootUrl = getAppRoot();
            axios
                .post(`${rootUrl}user/create`, this.$data)
                .then(response => {
                    if (response.data.message && response.data.status) {
                        alert(response.data.message);
                    }
                    window.location = this.redirect || rootUrl;
                })
                .catch(error => {
                    this.disableCreate = false;
                    this.messageVariant = "danger";
                    const message = error.response.data && error.response.data.err_msg;
                    this.messageText = message || "Registration failed for an unknown reason.";
                });
        }
    }
};
</script>
