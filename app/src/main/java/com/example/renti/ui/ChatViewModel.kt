package com.example.renti.ui

import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.renti.network.ChatRequest
import com.example.renti.network.ClientContext
import com.example.renti.network.ConversationCreateRequest
import com.example.renti.network.RetrofitClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ChatMessage(val text: String, val isUser: Boolean, val isCrisis: Boolean = false)

class ChatViewModel : ViewModel() {
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // Daftar pesan untuk dirender di UI
    val messages = mutableStateListOf<ChatMessage>()

    private val userId = "demo-user-001"
    private var conversationId: String? = null

    init {
        // Otomatis inisialisasi sesi percakapan saat ViewModel aktif
        initConversationSession()
    }

    fun initConversationSession(onComplete: (() -> Unit)? = null) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.apiService.createConversation(
                    ConversationCreateRequest(
                        userId = userId
                    )
                )
                conversationId = response.conversationId
                onComplete?.invoke()
            } catch (e: Exception) {
                // Sesi akan diinisialisasi ulang secara otomatis saat pengiriman pesan pertama
            }
        }
    }

    fun sendMessage(userText: String) {
        if (userText.isBlank()) return

        // 1. Tambahkan pesan user ke layar
        messages.add(ChatMessage(text = userText, isUser = true))
        _isLoading.value = true

        viewModelScope.launch {
            try {
                // 2. Pastikan sesi percakapan terdaftar di backend
                val activeConvId = conversationId ?: run {
                    val convResp = RetrofitClient.apiService.createConversation(
                        ConversationCreateRequest(
                            userId = userId
                        )
                    )
                    conversationId = convResp.conversationId
                    convResp.conversationId
                }

                // 3. Siapkan payload sesuai kontrak
                val request = ChatRequest(
                    userId = userId,
                    conversationId = activeConvId,
                    message = userText,
                    clientContext = ClientContext()
                )

                // 4. Panggil endpoint chat
                val response = RetrofitClient.apiService.sendMessage(request)

                // Cek apakah balasan merupakan peringatan krisis darurat (Signposting)
                val isCrisisMode = response.policyAction == "BLOCK_AND_SIGNPOST"

                messages.add(ChatMessage(
                    text = response.reply,
                    isUser = false,
                    isCrisis = isCrisisMode
                ))
            } catch (e: Exception) {
                messages.add(ChatMessage(
                    text = "Gagal terhubung ke Teman Curhat. Pastikan server aktif (${e.localizedMessage ?: "Network Error"}).",
                    isUser = false,
                    isCrisis = true
                ))
            } finally {
                _isLoading.value = false
            }
        }
    }
}