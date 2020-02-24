<template>
    <a
        class="panel-header-button"
        @click="showFavorites"
        v-b-tooltip.hover
        :title="tooltipText"
        href="javascript:void(0)"
    >
<!--      <span class="fa fa-star-o"></span>-->
      <span :class="['fa',isFavorites ? 'fa-star' : 'fa-star-o']"></span>
    </a>
</template>

<script>
import { VBTooltip } from "bootstrap-vue";

export default {
    name: "FavoritesButton",
    data() {
        return {
          // tooltipText: "Show favorites"
          tooltipText: "显示收藏夹",
          isFavorites: false
        };
    },
    directives: {
        "v-b-tooltip": VBTooltip
    },
    methods: {
        showFavorites() {
            // FIXME: use Vue communication for this
            const toolSearchQueryNode = document.querySelector(".tool-search-query");

            // if (toolSearchQueryNode.value.startsWith("#fav")) {
            if (toolSearchQueryNode.value.startsWith("#收藏")) {
                toolSearchQueryNode.value = "";
                toolSearchQueryNode.dispatchEvent(new Event("input"));
                // this.tooltipText = "Hide favorites";
                this.tooltipText = "显示收藏夹";
                this.isFavorites = false;
            } else {
                toolSearchQueryNode.value = "#收藏";
                toolSearchQueryNode.dispatchEvent(new Event("input"));
                // this.tooltipText = "隐藏收藏夹";
                this.tooltipText = "Show favorites";
                this.isFavorites = true;
            }
        }
    }
};
</script>

<style scoped></style>
