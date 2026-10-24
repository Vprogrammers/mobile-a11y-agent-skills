plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.compose.compiler)
}

android {
    namespace = "dev.vprogrammers.a11y.samples"
    compileSdk = 37

    defaultConfig {
        minSdk = 24
    }

    testOptions {
        unitTests.isIncludeAndroidResources = true
    }
}

/**
 * Eval fixtures are shown to agents without package or import lines. This task compiles
 * copies with a shared header so the fixtures stay valid Kotlin without changing them.
 */
abstract class GenerateEvalFixtures : DefaultTask() {
    @get:InputFiles
    abstract val fixtures: ConfigurableFileCollection

    @get:InputFile
    abstract val header: RegularFileProperty

    @get:OutputDirectory
    abstract val outputDir: DirectoryProperty

    @TaskAction
    fun generate() {
        val output = outputDir.get().asFile
        output.deleteRecursively()
        output.mkdirs()
        val prefix = header.get().asFile.readText()
        fixtures.files.forEach { fixture ->
            output.resolve(fixture.name).writeText(prefix + fixture.readText())
        }
    }
}

val generateEvalFixtures = tasks.register<GenerateEvalFixtures>("generateEvalFixtures") {
    val evals = rootDir.resolve("../../evals")
    // kmp-boundary-review is excluded: it intentionally mixes platform types in common code.
    fixtures.from(
        evals.resolve("android-compose-review/CheckoutScreen.kt"),
        evals.resolve("android-views-review/PaymentView.kt"),
        evals.resolve("clean-compose-review/AccessibleSettings.kt"),
        evals.resolve("clean-android-views-review/AccessibleRetryView.kt"),
    )
    header.set(layout.projectDirectory.file("eval-fixture-header.kt.txt"))
    outputDir.set(layout.buildDirectory.dir("generated/evalFixtures"))
}

androidComponents {
    onVariants { variant ->
        variant.sources.kotlin?.addGeneratedSourceDirectory(generateEvalFixtures, GenerateEvalFixtures::outputDir)
    }
}

dependencies {
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.foundation)
    implementation(libs.compose.material3)
    implementation(libs.compose.material.icons.core)
    implementation(libs.androidx.core)

    testImplementation(platform(libs.compose.bom))
    testImplementation(libs.compose.ui.test.junit4)
    testImplementation(libs.compose.ui.test.manifest)
    testImplementation(libs.compose.ui.test.junit4.accessibility)
    testImplementation(libs.activity.compose)
    testImplementation(libs.junit)
    testImplementation(libs.robolectric)
    testImplementation(libs.androidx.test.core)
}
