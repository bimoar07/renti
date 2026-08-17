package com.example.renti

import com.example.renti.network.ChatRequest
import com.example.renti.network.ChatResponse
import com.example.renti.network.ClientContext
import com.example.renti.network.ConversationCreateRequest
import com.example.renti.network.ConversationResponse
import com.example.renti.ui.ChatMessage
import com.google.gson.Gson
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ChatApiModelTest {

    private val gson = Gson()

    @Test
    fun testConversationCreateRequest_serialization() {
        val req = ConversationCreateRequest(userId = "demo-user-001", readinessStage = "contemplation")
        val json = gson.toJson(req)
        assertTrue(json.contains("\"user_id\":\"demo-user-001\""))
        assertTrue(json.contains("\"readiness_stage\":\"contemplation\""))
    }

    @Test
    fun testConversationResponse_deserialization() {
        val json = """
            {
                "conversation_id": "conv-12345",
                "user_id": "demo-user-001",
                "readiness_stage": "contemplation",
                "created_at": "2026-08-17T10:00:00Z"
            }
        """.trimIndent()

        val resp = gson.fromJson(json, ConversationResponse::class.java)
        assertEquals("conv-12345", resp.conversationId)
        assertEquals("demo-user-001", resp.userId)
        assertEquals("contemplation", resp.readinessStage)
    }

    @Test
    fun testChatRequest_serialization() {
        val req = ChatRequest(
            userId = "demo-user-001",
            conversationId = "conv-12345",
            message = "Aku lagi pengin ngerokok",
            clientContext = ClientContext(locationChip = "warkop", offline = false)
        )
        val json = gson.toJson(req)
        assertTrue(json.contains("\"user_id\":\"demo-user-001\""))
        assertTrue(json.contains("\"conversation_id\":\"conv-12345\""))
        assertTrue(json.contains("\"location_chip\":\"warkop\""))
    }

    @Test
    fun testChatResponse_normalAllow_deserialization() {
        val json = """
            {
                "conversation_id": "conv-12345",
                "reply": "Coba teknik 4-7-8 dulu ya.",
                "route": "zone_1_craving",
                "intent": "craving_support",
                "readiness_stage": "action",
                "policy_action": "ALLOW",
                "memory": {
                    "updated": true,
                    "context_tags": {"trigger": "warkop"}
                },
                "provider": {
                    "name": "primary",
                    "fallback_used": false
                }
            }
        """.trimIndent()

        val resp = gson.fromJson(json, ChatResponse::class.java)
        assertEquals("conv-12345", resp.conversationId)
        assertEquals("ALLOW", resp.policyAction)
        assertEquals("action", resp.readinessStage)
        assertNotNull(resp.memory)
        assertTrue(resp.memory?.updated == true)
        assertEquals("warkop", resp.memory?.contextTags?.get("trigger"))
    }

    @Test
    fun testChatResponse_crisisBlockAndSignpost_deserialization() {
        val json = """
            {
                "conversation_id": "conv-12345",
                "reply": "Hubungi 119 segera.",
                "route": "crisis",
                "intent": "crisis_support",
                "readiness_stage": "action",
                "policy_action": "BLOCK_AND_SIGNPOST",
                "memory": null,
                "provider": {
                    "name": "policy_fallback",
                    "fallback_used": true
                }
            }
        """.trimIndent()

        val resp = gson.fromJson(json, ChatResponse::class.java)
        assertEquals("BLOCK_AND_SIGNPOST", resp.policyAction)
        val isCrisis = resp.policyAction == "BLOCK_AND_SIGNPOST"
        val message = ChatMessage(text = resp.reply, isUser = false, isCrisis = isCrisis)
        assertTrue(message.isCrisis)
        assertFalse(message.isUser)
    }
}
