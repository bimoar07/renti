package com.example.renti.ui

import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.renti.network.ChatRequest
import com.example.renti.network.ClientContext
import com.example.renti.network.ConversationCreateRequest
import com.example.renti.network.RentiApiService
import com.example.renti.network.RetrofitClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

data class ChatMessage(
    val text: String,
    val isUser: Boolean,
    val isCrisis: Boolean = false,
    val isNetworkError: Boolean = false
)

class ChatViewModel(
    private val apiService: RentiApiService = RetrofitClient.apiService
) : ViewModel() {
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // Daftar pesan untuk dirender di UI
    val messages = mutableStateListOf<ChatMessage>()

    private val userId = "demo-user-001"
    private var conversationId: String? = null
    private val sessionMutex = Mutex()

    init {
        // Otomatis inisialisasi sesi percakapan saat ViewModel aktif
        viewModelScope.launch {
            try {
                getOrCreateConversationId()
            } catch (_: Exception) {
                // Sesi akan dibuat ulang secara transparan saat pesan pertama dikirim
            }
        }
    }

    suspend fun getOrCreateConversationId(): String {
        return sessionMutex.withLock {
            conversationId ?: run {
                val response = apiService.createConversation(
                    ConversationCreateRequest(userId = userId)
                )
                conversationId = response.conversationId
                response.conversationId
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
                // 2. Dapatkan ID percakapan aktif secara tersinkronisasi
                val activeConvId = getOrCreateConversationId()

                // 3. Siapkan payload sesuai kontrak
                val request = ChatRequest(
                    userId = userId,
                    conversationId = activeConvId,
                    message = userText,
                    clientContext = ClientContext()
                )

                // 4. Panggil endpoint chat
                val response = apiService.sendMessage(request)

                // Cek apakah balasan merupakan peringatan krisis darurat (Signposting)
                val isCrisisMode = response.policyAction == "BLOCK_AND_SIGNPOST"

                messages.add(ChatMessage(
                    text = response.reply,
                    isUser = false,
                    isCrisis = isCrisisMode
                ))
            } catch (e: Exception) {
                messages.add(ChatMessage(
                    text = "Tidak dapat terhubung ke Teman Curhat. Pastikan koneksi internet atau server demo backend aktif.",
                    isUser = false,
                    isCrisis = false,
                    isNetworkError = true
                ))
            } finally {
                _isLoading.value = false
            }
        }
    }
}