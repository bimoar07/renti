package com.example.renti.network

import com.google.gson.annotations.SerializedName

// Conversation Creation
data class ConversationCreateRequest(
    @SerializedName("user_id") val userId: String,
    @SerializedName("readiness_stage") val readinessStage: String? = null
)

data class ConversationResponse(
    @SerializedName("conversation_id") val conversationId: String,
    @SerializedName("user_id") val userId: String,
    @SerializedName("readiness_stage") val readinessStage: String,
    @SerializedName("created_at") val createdAt: String
)

// Request payload
data class ChatRequest(
    @SerializedName("user_id") val userId: String,
    @SerializedName("conversation_id") val conversationId: String,
    val message: String,
    @SerializedName("client_context") val clientContext: ClientContext
)

data class ClientContext(
    @SerializedName("location_chip") val locationChip: String = "warkop",
    val offline: Boolean = false
)

// Response payload
data class ChatResponse(
    @SerializedName("conversation_id") val conversationId: String,
    val reply: String,
    val route: String?,
    val intent: String?,
    @SerializedName("readiness_stage") val readinessStage: String,
    @SerializedName("policy_action") val policyAction: String, // ALLOW, BLOCK_AND_SIGNPOST, dll.
    val memory: MemoryData?,
    val provider: ProviderData?
)

data class MemoryData(
    val updated: Boolean,
    @SerializedName("context_tags") val contextTags: Map<String, String>?
)

data class ProviderData(
    val name: String,
    @SerializedName("fallback_used") val fallbackUsed: Boolean
)