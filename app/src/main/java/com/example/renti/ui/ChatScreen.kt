package com.example.renti.ui

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.renti.ui.theme.RentiTheme

/**
 * Stateful ChatScreen yang terhubung ke ChatViewModel.
 */
@Composable
fun ChatScreen(
    modifier: Modifier = Modifier,
    viewModel: ChatViewModel = viewModel()
) {
    val isLoading by viewModel.isLoading.collectAsState()

    ChatContent(
        messages = viewModel.messages,
        isLoading = isLoading,
        onSendMessage = { text -> viewModel.sendMessage(text) },
        modifier = modifier
    )
}

/**
 * Stateless ChatContent untuk rendering murni UI dan Compose Preview.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatContent(
    messages: List<ChatMessage>,
    isLoading: Boolean,
    onSendMessage: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var inputText by rememberSaveable { mutableStateOf("") }
    val listState = rememberLazyListState()

    // Otomatis scroll ke pesan terbawah setiap kali ada pesan baru
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Teman Curhat") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .fillMaxSize()
        ) {
            // Area Obrolan
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(vertical = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(messages) { msg ->
                    ChatBubble(msg)
                }
            }

            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier
                        .align(Alignment.CenterHorizontally)
                        .padding(8.dp)
                )
            }

            // Area Input Teks
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Ketik curhatanmu...") },
                    shape = RoundedCornerShape(24.dp),
                    keyboardOptions = KeyboardOptions(
                        imeAction = ImeAction.Send
                    ),
                    keyboardActions = KeyboardActions(
                        onSend = {
                            if (inputText.isNotBlank() && !isLoading) {
                                onSendMessage(inputText)
                                inputText = ""
                            }
                        }
                    ),
                    maxLines = 4
                )
                Spacer(modifier = Modifier.width(8.dp))
                Button(
                    onClick = {
                        if (inputText.isNotBlank()) {
                            onSendMessage(inputText)
                            inputText = ""
                        }
                    },
                    enabled = !isLoading && inputText.isNotBlank()
                ) {
                    Text("Kirim")
                }
            }
        }
    }
}

@Composable
fun ChatBubble(message: ChatMessage) {
    val context = LocalContext.current

    val bubbleColor = when {
        message.isCrisis -> MaterialTheme.colorScheme.errorContainer // Merah jika krisis (Signposting)
        message.isNetworkError -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.7f)
        message.isUser -> MaterialTheme.colorScheme.primary          // Oranye/Primary jika user
        else -> MaterialTheme.colorScheme.surfaceVariant             // Netral jika AI
    }

    val textColor = when {
        message.isCrisis -> MaterialTheme.colorScheme.onErrorContainer
        message.isNetworkError -> MaterialTheme.colorScheme.error
        message.isUser -> MaterialTheme.colorScheme.onPrimary
        else -> MaterialTheme.colorScheme.onSurfaceVariant
    }

    Box(
        modifier = Modifier.fillMaxWidth(),
        contentAlignment = if (message.isUser) Alignment.CenterEnd else Alignment.CenterStart
    ) {
        Column(
            modifier = Modifier
                .widthIn(max = 320.dp)
                .background(
                    color = bubbleColor,
                    shape = RoundedCornerShape(16.dp)
                )
                .padding(12.dp)
        ) {
            Text(
                text = message.text,
                color = textColor,
                style = MaterialTheme.typography.bodyMedium
            )

            // Jika mode krisis (Signposting), sediakan tombol cepat panggilan darurat 119
            if (message.isCrisis) {
                Spacer(modifier = Modifier.height(8.dp))
                Button(
                    onClick = {
                        val dialIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:119"))
                        context.startActivity(dialIntent)
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    ),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Text("📞 Hubungi Hotline 119", style = MaterialTheme.typography.labelMedium)
                }
            }
        }
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun ChatScreenPreview() {
    val mockMessages = listOf(
        ChatMessage(
            text = "Halo Renti, aku lagi pengin banget ngerokok di warkop.",
            isUser = true
        ),
        ChatMessage(
            text = "Aku paham banget godaannya saat di warkop. Coba teknik 4-7-8 dulu atau minum air putih dingin ya. Kamu sudah bertahan sejauh ini!",
            isUser = false
        ),
        ChatMessage(
            text = "Peringatan: Jika Anda sedang berada dalam kondisi darurat kesehatan, segera hubungi Layanan Berhenti Merokok Kemenkes 0-800-177-6565 atau 119.",
            isUser = false,
            isCrisis = true
        )
    )

    RentiTheme {
        ChatContent(
            messages = mockMessages,
            isLoading = false,
            onSendMessage = {}
        )
    }
}