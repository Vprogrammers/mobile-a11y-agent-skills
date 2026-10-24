class AccessibleRetryView(
    context: Context,
    onRetry: () -> Unit,
) : LinearLayout(context) {
    private val status = TextView(context).apply {
        text = "Connection failed"
    }
    private val retry = Button(context).apply {
        text = "Retry"
        setOnClickListener { onRetry() }
    }

    init {
        orientation = VERTICAL
        addView(status)
        addView(retry)
    }
}
