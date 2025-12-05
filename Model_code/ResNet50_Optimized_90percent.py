# ============================================================
# ResNet50 Fine-tuning 최적화 코드 (목표: 90% 정확도)
# ============================================================

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import numpy as np

# GPU 메모리 증가 방지 설정
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# -----------------------------
# 1. 데이터 경로 설정
# -----------------------------
train_dir = "/content/drive/MyDrive/brain_ct/train"
test_dir = "/content/drive/MyDrive/brain_ct/test"

img_size = (224, 224)
batch_size = 32

# -----------------------------
# 2. 강화된 Data Augmentation
# -----------------------------
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,           # 10 → 20 증가
    width_shift_range=0.15,      # 새로 추가
    height_shift_range=0.15,     # 새로 추가
    horizontal_flip=True,
    zoom_range=0.2,              # 0.1 → 0.2 증가
    brightness_range=[0.8, 1.2], # 밝기 조정 추가
    fill_mode='nearest'
)

test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary',
    shuffle=True
)

test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary',
    shuffle=False
)

# 클래스 분포 확인
print("\n=== 데이터셋 정보 ===")
print(f"Train samples: {train_generator.samples}")
print(f"Test samples: {test_generator.samples}")
print(f"Class indices: {train_generator.class_indices}")
print(f"Class distribution: {np.bincount(train_generator.classes)}")

# -----------------------------
# 3. Class Weights 계산 (클래스 불균형 처리)
# -----------------------------
from sklearn.utils.class_weight import compute_class_weight

# 현재 데이터: hemorrhage(2152) vs normal(3371)
# hemorrhage에 더 높은 가중치 부여
class_weights_array = compute_class_weight(
    'balanced',
    classes=np.unique(train_generator.classes),
    y=train_generator.classes
)

# hemorrhage 가중치 추가 강화 (1.5배)
class_weights = {
    0: class_weights_array[0],
    1: class_weights_array[1] * 1.3  # hemorrhage 가중치 30% 추가
}

print(f"\nClass weights: {class_weights}")

# -----------------------------
# 4. ResNet50 Fine-tuning 모델 구성 (2단계)
# -----------------------------
def create_resnet50_model(input_shape=(224, 224, 3), trainable_base=False):
    """
    ResNet50 Fine-tuning 모델 생성

    Args:
        input_shape: 입력 이미지 크기
        trainable_base: True면 base model 일부 학습, False면 freeze
    """
    # ImageNet pretrained ResNet50
    base_model = ResNet50(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )

    # Base model freeze 설정
    if not trainable_base:
        # Stage 1: 전체 freeze
        for layer in base_model.layers:
            layer.trainable = False
    else:
        # Stage 2: 마지막 30개 레이어만 unfreeze
        for layer in base_model.layers[:-30]:
            layer.trainable = False
        for layer in base_model.layers[-30:]:
            layer.trainable = True

    # Top layers 추가
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)  # 128 → 256 증가
    x = Dropout(0.5)(x)  # 0.3 → 0.5 증가 (overfitting 방지)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(1, activation='sigmoid')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    return model, base_model

# -----------------------------
# 5. Callbacks 설정
# -----------------------------
callbacks_stage1 = [
    EarlyStopping(
        monitor='val_loss',
        patience=3,
        restore_best_weights=True,
        verbose=1
    ),
    ModelCheckpoint(
        filepath='/content/drive/MyDrive/resnet50_stage1_best.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

callbacks_stage2 = [
    EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    ),
    ModelCheckpoint(
        filepath='/content/drive/MyDrive/resnet50_stage2_best.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

# -----------------------------
# 6. Stage 1 학습 (Base model freeze)
# -----------------------------
print("\n" + "="*60)
print("🚀 Stage 1: Top layers만 학습 (Base model freeze)")
print("="*60)

model, base_model = create_resnet50_model(trainable_base=False)

model.compile(
    optimizer=Adam(learning_rate=1e-3),  # 높은 LR로 빠르게 학습
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print(f"\nTrainable parameters: {sum([np.prod(v.get_shape()) for v in model.trainable_weights]):,}")
print(f"Non-trainable parameters: {sum([np.prod(v.get_shape()) for v in model.non_trainable_weights]):,}")

history_stage1 = model.fit(
    train_generator,
    validation_data=test_generator,
    epochs=5,
    class_weight=class_weights,
    callbacks=callbacks_stage1,
    verbose=1
)

# Stage 1 결과 출력
val_acc_stage1 = max(history_stage1.history['val_accuracy'])
print(f"\n✅ Stage 1 완료 - 최고 검증 정확도: {val_acc_stage1*100:.2f}%")

# -----------------------------
# 7. Stage 2 학습 (마지막 레이어 unfreeze)
# -----------------------------
print("\n" + "="*60)
print("🚀 Stage 2: 마지막 Conv block fine-tuning")
print("="*60)

# 마지막 30개 레이어 언프리즈
for layer in base_model.layers[-30:]:
    layer.trainable = True

model.compile(
    optimizer=Adam(learning_rate=1e-4),  # 낮은 LR로 섬세하게 fine-tuning
    loss='binary_crossentropy',
    metrics=['accuracy']
)

print(f"\nTrainable parameters: {sum([np.prod(v.get_shape()) for v in model.trainable_weights]):,}")
print(f"Non-trainable parameters: {sum([np.prod(v.get_shape()) for v in model.non_trainable_weights]):,}")

history_stage2 = model.fit(
    train_generator,
    validation_data=test_generator,
    epochs=25,
    class_weight=class_weights,
    callbacks=callbacks_stage2,
    verbose=1
)

# Stage 2 결과 출력
val_acc_stage2 = max(history_stage2.history['val_accuracy'])
print(f"\n✅ Stage 2 완료 - 최고 검증 정확도: {val_acc_stage2*100:.2f}%")

# -----------------------------
# 8. 최종 모델 저장
# -----------------------------
model.save("/content/drive/MyDrive/resnet50_final_optimized.h5")
print("\n💾 최종 모델 저장 완료: resnet50_final_optimized.h5")

# -----------------------------
# 9. 최종 평가
# -----------------------------
print("\n" + "="*60)
print("📊 최종 모델 평가")
print("="*60)

loss, accuracy = model.evaluate(test_generator, verbose=1)
print(f"\n최종 Test Loss: {loss:.4f}")
print(f"최종 Test Accuracy: {accuracy*100:.2f}%")

if accuracy >= 0.90:
    print("\n🎉 목표 달성! 90% 이상 정확도 달성!")
else:
    print(f"\n⚠️  현재 {accuracy*100:.2f}% - 90% 목표까지 {(0.90-accuracy)*100:.2f}% 부족")

# -----------------------------
# 10. 예측 테스트
# -----------------------------
from tensorflow.keras.preprocessing import image

print("\n" + "="*60)
print("🔍 실제 이미지 예측 테스트")
print("="*60)

# hemorrhage 이미지 테스트
img_path_hem = "/content/drive/MyDrive/brain_ct/test/hemorrhage/ds1_0_hemorrhage_1026_IMG-0001-00073.jpg"
img_hem = image.load_img(img_path_hem, target_size=img_size)
x_hem = image.img_to_array(img_hem)
x_hem = np.expand_dims(x_hem, axis=0)
x_hem = x_hem / 255.0

pred_hem = model.predict(x_hem)[0][0]
label_hem = "hemorrhage" if pred_hem >= 0.5 else "normal"
print(f"\n1. Hemorrhage 이미지 예측:")
print(f"   - 예측값: {pred_hem:.4f}")
print(f"   - 판정: {label_hem}")
print(f"   - 정답: hemorrhage")
print(f"   - 결과: {'✅ 정답' if label_hem == 'hemorrhage' else '❌ 오답'}")

# normal 이미지 테스트 (파일 경로는 실제 경로로 수정 필요)
try:
    import glob
    normal_images = glob.glob("/content/drive/MyDrive/brain_ct/test/normal/*.jpg")
    if normal_images:
        img_path_normal = normal_images[0]
        img_normal = image.load_img(img_path_normal, target_size=img_size)
        x_normal = image.img_to_array(img_normal)
        x_normal = np.expand_dims(x_normal, axis=0)
        x_normal = x_normal / 255.0

        pred_normal = model.predict(x_normal)[0][0]
        label_normal = "hemorrhage" if pred_normal >= 0.5 else "normal"
        print(f"\n2. Normal 이미지 예측:")
        print(f"   - 예측값: {pred_normal:.4f}")
        print(f"   - 판정: {label_normal}")
        print(f"   - 정답: normal")
        print(f"   - 결과: {'✅ 정답' if label_normal == 'normal' else '❌ 오답'}")
except:
    print("\n2. Normal 이미지 테스트를 위한 경로를 확인해주세요.")

# -----------------------------
# 11. 학습 곡선 시각화
# -----------------------------
import matplotlib.pyplot as plt

# Stage 2 학습 곡선
plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.plot(history_stage2.history['accuracy'], label='Train Accuracy')
plt.plot(history_stage2.history['val_accuracy'], label='Val Accuracy')
plt.axhline(y=0.90, color='r', linestyle='--', label='90% Goal')
plt.title('Model Accuracy (Stage 2)')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(history_stage2.history['loss'], label='Train Loss')
plt.plot(history_stage2.history['val_loss'], label='Val Loss')
plt.title('Model Loss (Stage 2)')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('/content/drive/MyDrive/training_curves.png', dpi=300, bbox_inches='tight')
print("\n📈 학습 곡선 저장 완료: training_curves.png")
plt.show()

print("\n" + "="*60)
print("✨ 모든 학습 완료!")
print("="*60)
