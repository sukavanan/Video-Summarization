import torch
import warnings
from model.model import *
from model.config import *
from model.misc import *
warnings.filterwarnings("ignore")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train(train_loader, dev_loader):
    model = bLSTM(input_dim, hidden_dim, linear_dim, output_dim).to(device)
    model.init_weights()
    loss_fn = torch.nn.CrossEntropyLoss(ignore_index = -1).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr = 0.01)
    epochs = 10
    dev_max_acc = 0

    for epoch in range(epochs):
        model.train()
        train_acc = 0.0
        dev_acc = 0.0
        batch = 0
        for inputs, target in train_loader:
            print(batch, end = "\r")
            batch += 1
            inputs, target = inputs.to(device), target.to(device)
            optimizer.zero_grad()
            lens = get_lengths(target, -1)
            output = model(inputs, lens)
            output = output.view(-1, output.shape[-1])
            target = target.view(-1)
            loss = loss_fn(output, target)
            loss.backward()
            optimizer.step()
            train_acc += float(accuracy(output, target).item())
        
        model.eval()
        for inputs, target in dev_loader:
            inputs, target = inputs.to(device), target.to(device)
            inputs, target = inputs, target
            lens = get_lengths(target, -1)
            output = model(inputs, lens)
            output = output.view(-1, output.shape[-1])
            target = target.view(-1)
            loss = loss_fn(output, target)
            dev_acc += float(accuracy(output, target).item())
        
        train_acc = (train_acc * batch_size)/len(train_loader.dataset)
        dev_acc = (dev_acc * batch_size)/len(dev_loader.dataset)
        
        print('Epoch: {} \tTraining Acc: {:.6f} \tDev Set Acc: {:.6f}'.format(epoch+1, train_acc,dev_acc))
        if dev_acc >= dev_max_acc:
            print('Dev Set acc increased ({:.6f} --> {:.6f}). Saving model...'.format(dev_max_acc, dev_acc))
            torch.save(model.state_dict(), 'model.pt')
            dev_max_acc = dev_acc
    
    del model, optimizer, loss_fn